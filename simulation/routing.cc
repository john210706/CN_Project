#include "routing.h"

#include "ns3/inet-socket-address.h"
#include "ns3/simulator.h"
#include "ns3/udp-socket-factory.h"

#include <filesystem>
#include <iomanip>

namespace lab
{
using namespace ns3;

static double
Now()
{
    return Simulator::Now().GetSeconds() * 1000;
}

Trace::Trace(const std::string& p)
{
    std::filesystem::create_directories(p);
    events.open(p + "/packet_events.csv");
    positions.open(p + "/node_positions.csv");
    radio.open(p + "/radio_events.csv");
    if (!events || !positions || !radio)
    {
        throw std::runtime_error("Cannot open trace output");
    }
    events << "simulation_time_ms,event_type,packet_id,source_id,destination_id,current_node_id,"
              "previous_forwarder_id,traffic_class,creation_time_ms,expiry_time_ms,remaining_time_"
              "ms,hop_count,payload_bytes,candidate_score,estimated_remaining_delay_ms,forwarding_"
              "wait_ms,queue_delay_ms,link_quality,normalized_progress,slack_ms,drop_reason\n"
           << std::setprecision(12);
    positions << "simulation_time_ms,node_id,x,y,z\n" << std::setprecision(12);
    radio << "simulation_time_ms,node_id,event_type,bytes,reason\n" << std::setprecision(12);
}

void
Trace::Event(const std::string& type,
             const Header& h,
             uint32_t node,
             const std::string& reason,
             const Decision& d)
{
    events << Now() << ',' << type << ',' << h.Id() << ',' << h.source << ',' << h.destination
           << ',' << node << ',' << h.last << ',' << unsigned(h.trafficClass) << ','
           << h.created / 1e6 << ',' << h.expiry / 1e6 << ','
           << (double(h.expiry) - Simulator::Now().GetNanoSeconds()) / 1e6 << ',' << h.hops << ','
           << h.payload << ',' << d.score << ',' << d.estimate << ',' << d.wait << ','
           << d.queueDelay << ',' << d.link << ',' << d.progress << ',' << d.slack << ',' << reason
           << '\n';
}

NS_OBJECT_ENSURE_REGISTERED(Routing);

TypeId
Routing::GetTypeId()
{
    static TypeId t = TypeId("lab::Routing").SetParent<Application>().AddConstructor<Routing>();
    return t;
}

void
Routing::Setup(uint32_t id,
               const Config* c,
               Trace* t,
               const std::vector<Vector>& initial,
               const std::vector<std::vector<uint32_t>>& routes)
{
    id_ = id;
    c_ = c;
    t_ = t;
    initial_ = initial;
    routes_ = routes;
    random_ = CreateObject<UniformRandomVariable>();
    random_->SetStream(4000 + id);
}

void
Routing::StartApplication()
{
    socket_ = Socket::CreateSocket(GetNode(), UdpSocketFactory::GetTypeId());
    socket_->SetAllowBroadcast(true);
    if (socket_->Bind(InetSocketAddress(Ipv4Address::GetAny(), 9000)) < 0)
    {
        throw std::runtime_error("UDP bind failed");
    }
    socket_->SetRecvCallback(MakeCallback(&Routing::Receive, this));
    helloEvent_ = Simulator::Schedule(Seconds(.01 + id_ * 0.001), &Routing::Hello, this);
    cleanEvent_ = Simulator::Schedule(Seconds(1), &Routing::Cleanup, this);
}

void
Routing::StopApplication()
{
    Simulator::Cancel(helloEvent_);
    Simulator::Cancel(cleanEvent_);
    for (auto& [key, s] : states_)
    {
        Simulator::Cancel(s.event);
        Simulator::Cancel(s.expiryEvent);
    }
    if (socket_)
    {
        socket_->Close();
    }
}

double
Routing::Processing() const
{
    return c_->topology == "diamond" && id_ == 1 ? c_->slowProcessing : c_->processing;
}

void
Routing::Hello()
{
    Header h;
    h.kind = 1;
    h.source = h.last = id_;
    h.beacon = ++beacon_;
    h.queue = pending_;
    h.processingUs = Processing() * 1000;
    auto p = GetNode()->GetObject<MobilityModel>()->GetPosition();
    h.x = std::lround(p.x * 1000);
    h.y = std::lround(p.y * 1000);
    auto packet = Create<Packet>();
    packet->AddHeader(h);
    if (socket_->SendTo(packet, 0, InetSocketAddress(Ipv4Address("255.255.255.255"), 9000)) >= 0)
    {
        t_->Event("CONTROL_TX", h, id_);
    }
    helloEvent_ = Simulator::Schedule(Seconds(c_->hello), &Routing::Hello, this);
}

void
Routing::Cleanup()
{
    auto now = Simulator::Now().GetNanoSeconds();
    for (auto it = states_.begin(); it != states_.end();)
    {
        if (!it->second.pending && it->second.retainUntil < now)
        {
            it = states_.erase(it);
        }
        else
        {
            ++it;
        }
    }
    for (auto it = neighbors_.begin(); it != neighbors_.end();)
    {
        if (now - it->second.updated > int64_t(5 * c_->hello * 1e9))
        {
            it = neighbors_.erase(it);
        }
        else
        {
            ++it;
        }
    }
    cleanEvent_ = Simulator::Schedule(Seconds(1), &Routing::Cleanup, this);
}

double
Routing::Quality(uint32_t sender)
{
    auto it = neighbors_.find(sender);
    if (it == neighbors_.end())
    {
        return 0.;
    }
    auto& n = it->second;
    auto now = Simulator::Now().GetNanoSeconds();
    while (!n.beacons.empty() && now - n.beacons.front().second > int64_t(10 * c_->hello * 1e9))
    {
        n.beacons.pop_front();
    }
    if (n.beacons.empty())
    {
        return 0.;
    }
    auto missed = uint32_t(std::max(0., (Now() - n.updated / 1e6) / (c_->hello * 1000) - .2));
    return std::clamp(double(n.beacons.size()) / (n.last - n.beacons.front().first + 1 + missed),
                      0.,
                      1.);
}

void
Routing::Generate(uint32_t dest, uint8_t cls, double lifetime)
{
    Header h;
    h.source = id_;
    h.destination = dest;
    h.sequence = ++sequence_;
    h.last = id_;
    h.trafficClass = cls;
    h.payload = c_->payload;
    h.created = Simulator::Now().GetNanoSeconds();
    h.expiry = h.created + uint64_t(std::llround(lifetime * 1e6));
    h.limit = c_->maxHops;
    h.dx = std::lround(initial_[dest].x * 1000);
    h.dy = std::lround(initial_[dest].y * 1000);
    t_->Event("PACKET_CREATED", h, id_);
    Schedule(h, {}, true);
}

void
Routing::Schedule(Header h, Decision d, bool origin)
{
    auto key = h.Id();
    if (pending_ >= c_->queueCapacity)
    {
        t_->Event("PACKET_DROPPED", h, id_, "QUEUE_OVERFLOW");
        return;
    }
    double now = Now();
    double processing = Processing();
    double serviceStart = std::max(now, serviceFree_);
    d.queueDelay = serviceStart - now;
    serviceFree_ = serviceStart + processing;
    // Holdoff overlaps other jobs' processing, but each processing job reserves a serial server
    // slot.
    double delay = d.queueDelay + processing + (origin ? 0 : d.wait);
    auto& s = states_[key];
    s.h = h;
    s.pending = true;
    s.retainUntil =
        int64_t(h.expiry +
                (c_->maxHops * (c_->queueCapacity * std::max(c_->processing, c_->slowProcessing) +
                                c_->maxHoldoff) +
                 1000) *
                    1e6);
    ++pending_;
    s.event = Simulator::Schedule(Seconds(delay / 1000), &Routing::Forward, this, key);
    if (c_->protocol == "deadline_aware")
    {
        s.expiryEvent =
            Simulator::Schedule(NanoSeconds(h.expiry - Simulator::Now().GetNanoSeconds()),
                                &Routing::Expire,
                                this,
                                key);
    }
    t_->Event("FORWARD_SCHEDULED", h, id_, "", d);
}

void
Routing::Expire(uint64_t key)
{
    auto it = states_.find(key);
    if (it == states_.end() || !it->second.pending)
    {
        return;
    }
    auto& s = it->second;
    Simulator::Cancel(s.event);
    s.pending = false;
    --pending_;
    t_->Event("FORWARD_CANCELLED", s.h, id_, "EXPIRED_BEFORE_FORWARD");
    t_->Event("PACKET_EXPIRED", s.h, id_, "EXPIRED_BEFORE_FORWARD");
}

void
Routing::Forward(uint64_t key)
{
    auto& s = states_.at(key);
    if (!s.pending)
    {
        return;
    }
    if (c_->protocol == "deadline_aware" &&
        Simulator::Now().GetNanoSeconds() >= int64_t(s.h.expiry))
    {
        Expire(key);
        return;
    }
    Simulator::Cancel(s.expiryEvent);
    s.pending = false;
    --pending_;
    s.forwarded = true;
    auto h = s.h;
    h.last = id_;
    h.hops++;
    h.next = c_->protocol == "fixed" ? routes_[id_][h.destination] : UINT32_MAX;
    if (c_->protocol == "fixed" && h.next == UINT32_MAX)
    {
        t_->Event("PACKET_DROPPED", h, id_, "NO_FORWARDING_CANDIDATE");
        return;
    }
    auto p = GetNode()->GetObject<MobilityModel>()->GetPosition();
    h.x = std::lround(p.x * 1000);
    h.y = std::lround(p.y * 1000);
    t_->Event("FORWARD_EXECUTED", h, id_);
    Transmit(h);
}

void
Routing::Transmit(Header h)
{
    auto p = Create<Packet>(h.payload);
    p->AddHeader(h);
    t_->Event("TX_ATTEMPT", h, id_);
    if (socket_->SendTo(p, 0, InetSocketAddress(Ipv4Address("255.255.255.255"), 9000)) >= 0)
    {
        t_->Event("PACKET_TX", h, id_);
    }
    else
    {
        t_->Event("PACKET_DROPPED", h, id_, "SOCKET_ERROR");
    }
}

void
Routing::Receive(Ptr<Socket> socket)
{
    while (auto p = socket->Recv())
    {
        Header h;
        if (p->GetSize() < h.GetSerializedSize() || p->RemoveHeader(h) != h.GetSerializedSize() ||
            !h.Valid(c_->nodes))
        {
            t_->Event("PACKET_DROPPED", h, id_, "INVALID_PACKET");
            continue;
        }
        if (h.last == id_)
        {
            continue;
        }
        // Explicit, separately logged receiver fault injection; default disabled.
        if (id_ == c_->lossNode && random_->GetValue() < c_->loss)
        {
            t_->Event("FAULT_DROP", h, id_, "INJECTED_LOSS");
            continue;
        }
        if (h.kind == 1)
        {
            auto& n = neighbors_[h.last];
            if (h.beacon > n.last)
            {
                n.last = h.beacon;
                n.updated = Simulator::Now().GetNanoSeconds();
                n.beacons.emplace_back(h.beacon, n.updated);
            }
            t_->Event("CONTROL_RX", h, id_);
            continue;
        }
        if (p->GetSize() != h.payload)
        {
            t_->Event("PACKET_DROPPED", h, id_, "INVALID_PACKET");
            continue;
        }
        t_->Event("PACKET_RX", h, id_);
        if (Now() >
            h.expiry / 1e6 +
                c_->maxHops * (c_->queueCapacity * std::max(c_->processing, c_->slowProcessing) +
                               c_->maxHoldoff) +
                1000)
        {
            t_->Event("PACKET_DROPPED", h, id_, "HISTORY_HORIZON");
            continue;
        }
        auto it = states_.find(h.Id());
        if (it != states_.end())
        {
            // Only a received downstream forward cancels a pending timer. No global notifications.
            if (it->second.pending && h.hops > it->second.h.hops)
            {
                Simulator::Cancel(it->second.event);
                Simulator::Cancel(it->second.expiryEvent);
                it->second.pending = false;
                --pending_;
                t_->Event("FORWARD_CANCELLED", h, id_, "OVERHEARD_FORWARD");
                t_->Event("DUPLICATE_SUPPRESSED", h, id_);
            }
            t_->Event("PACKET_DROPPED", h, id_, "DUPLICATE");
            continue;
        }
        if (c_->protocol == "fixed" && h.next != id_)
        {
            continue;
        }
        if (h.destination == id_)
        {
            State s;
            s.h = h;
            s.retainUntil = int64_t(
                h.expiry +
                (c_->maxHops * (c_->queueCapacity * std::max(c_->processing, c_->slowProcessing) +
                                c_->maxHoldoff) +
                 1000) *
                    1e6);
            states_[h.Id()] = s;
            t_->Event("DESTINATION_DELIVERED", h, id_);
            continue;
        }
        if (h.source == id_)
        {
            continue;
        }
        if (c_->protocol == "deadline_aware" &&
            Simulator::Now().GetNanoSeconds() >= int64_t(h.expiry))
        {
            t_->Event("PACKET_EXPIRED", h, id_, "EXPIRED_ON_RECEIVE");
            continue;
        }
        if (h.hops >= h.limit)
        {
            t_->Event("PACKET_DROPPED", h, id_, "HOP_LIMIT");
            continue;
        }
        auto pos = GetNode()->GetObject<MobilityModel>()->GetPosition();
        double before = std::hypot((h.x - h.dx) / 1000., (h.y - h.dy) / 1000.);
        double dist = std::hypot(pos.x - h.dx / 1000., pos.y - h.dy / 1000.);
        auto d = Select(*c_,
                        Quality(h.last),
                        before - dist,
                        dist,
                        std::max(0., serviceFree_ - Now()),
                        Processing(),
                        h.expiry / 1e6 - Now());
        if (c_->protocol == "fixed")
        {
            d.eligible = true;
            d.wait = 0;
            d.reason = "";
        }
        // A tiny stable node/packet tie-break is independent of NS-3's RNG consumption.
        d.wait += ((h.Id() * 2654435761ULL + id_ * 2246822519ULL + c_->seed) % 1000) * 1e-6;
        t_->Event("CANDIDATE_EVALUATED", h, id_, d.reason, d);
        if (d.eligible)
        {
            Schedule(h, d);
        }
        else
        {
            t_->Event("PACKET_DROPPED", h, id_, d.reason, d);
        }
    }
}
} // namespace lab
