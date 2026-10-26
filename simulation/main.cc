#include "routing.h"

#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/netanim-module.h"
#include "ns3/network-module.h"
#include "ns3/wifi-module.h"

#include <filesystem>
#include <iostream>
#include <queue>
#include <sstream>
using namespace ns3;
using namespace lab;

static void
Require(bool v, const char* msg)
{
    if (!v)
    {
        throw std::runtime_error(msg);
    }
}

static void
SelfTest()
{
    lab::Header h;
    h.source = 2;
    h.destination = 3;
    h.last = 1;
    h.sequence = 4000000000U;
    h.created = 123456789;
    h.expiry = 987654321;
    h.hops = 7;
    h.x = -12345;
    h.y = 67890;
    auto p = Create<Packet>(100);
    p->AddHeader(h);
    Require(p->GetSize() == 176, "header size");
    lab::Header out;
    p->RemoveHeader(out);
    Require(out.Id() == h.Id() && out.created == h.created && out.expiry == h.expiry &&
                out.hops == 7 && out.x == h.x && out.y == h.y && out.Valid(4),
            "header roundtrip");
    out.version = 9;
    Require(!out.Valid(4), "invalid version");
    out = h;
    out.destination = 8;
    Require(!out.Valid(4), "invalid destination");
    lab::Config c;
    auto a = Select(c, .8, 50, 60, 0, 1, 50), b = Select(c, .8, 50, 60, 20, 1, 50);
    Require(a.score > b.score && a.score <= 1 && a.score >= 0, "delay preference");
    Require(!Select(c, 1, 30, 30, 0, 1, 0).eligible && !Select(c, 1, 30, 30, 0, 1, -1).eligible,
            "expired feasibility");
    Require(!Select(c, 1, 30, 30, 0, 1, 1).eligible, "zero slack");
    c.protocol = "opportunistic";
    Require(Select(c, .8, 50, 60, 0, 1, 1).score == Select(c, .8, 50, 60, 0, 1, 500).score,
            "baseline deadline independence");
    c.weights[0] = -1;
    bool rejected = false;
    try
    {
        c.Validate();
    }
    catch (...)
    {
        rejected = true;
    }
    Require(rejected, "negative weights");
    std::cout
        << "C++ self-tests passed: serialization, invalid header, feasibility, scoring, weights\n";
}

static void
Positions(NodeContainer nodes, Trace* trace, double until)
{
    for (uint32_t i = 0; i < nodes.GetN(); ++i)
    {
        auto p = nodes.Get(i)->GetObject<MobilityModel>()->GetPosition();
        trace->positions << Simulator::Now().GetSeconds() * 1000 << ',' << i << ',' << p.x << ','
                         << p.y << ',' << p.z << '\n';
    }
    if (Simulator::Now().GetSeconds() + .1 < until)
    {
        Simulator::Schedule(Seconds(.1), &Positions, nodes, trace, until);
    }
}

static void
PhyTx(Trace* t, uint32_t id, Ptr<const Packet> p, double)
{
    t->radio << Simulator::Now().GetSeconds() * 1000 << ',' << id << ",PHY_TX_BEGIN,"
             << p->GetSize() << ",\n";
}

static void
PhyDrop(Trace* t, uint32_t id, Ptr<const Packet> p, WifiPhyRxfailureReason reason)
{
    t->radio << Simulator::Now().GetSeconds() * 1000 << ',' << id << ",PHY_RX_DROP," << p->GetSize()
             << ',' << int(reason) << '\n';
}

static void
Arrival(Ptr<Routing> app,
        uint32_t dest,
        const lab::Config* c,
        Ptr<UniformRandomVariable> cls,
        Ptr<ExponentialRandomVariable> poisson)
{
    double u = cls->GetValue(), sum = 0;
    uint8_t k = 0;
    for (; k < 3; k++)
    {
        sum += c->mix[k];
        if (u < sum)
        {
            break;
        }
    }
    app->Generate(dest, k, c->deadline > 0 ? c->deadline : c->deadlines[k]);
    double dt = c->traffic == "poisson" ? poisson->GetValue() : 1 / c->rate;
    if (Simulator::Now().GetSeconds() + dt < c->stop)
    {
        Simulator::Schedule(Seconds(dt), &Arrival, app, dest, c, cls, poisson);
    }
}

static void
ParseArray(const std::string& text, std::array<double, 4>& a)
{
    std::stringstream s(text);
    std::string part;
    size_t i = 0;
    while (std::getline(s, part, ','))
    {
        if (i >= 4)
        {
            throw std::runtime_error("Expected four comma-separated numbers");
        }
        size_t n = 0;
        a[i++] = std::stod(part, &n);
        if (n != part.size())
        {
            throw std::runtime_error("Invalid numeric list");
        }
    }
    if (i != 4)
    {
        throw std::runtime_error("Expected four comma-separated numbers");
    }
}

int
main(int argc, char** argv)
{
    try
    {
        lab::Config c;
        bool selfTest = false;
        std::string weights = "0.3,0.3,0.3,0.1", mix = "0.25,0.25,0.25,0.25",
                    deadlines = "50,100,500,1000", pairs;
        CommandLine cmd(__FILE__);
#define ARG(field, description) cmd.AddValue(#field, description, c.field)
        ARG(protocol, "fixed, opportunistic, deadline_aware");
        ARG(topology, "diamond, line, grid, random, mobile");
        ARG(nodes, "Number of Wi-Fi nodes");
        ARG(mobility, "static, waypoint, velocity");
        ARG(traffic, "constant or poisson");
        ARG(output, "Empty output directory");
        ARG(rateMode, "802.11a OFDM rate");
        ARG(seed, "NS-3 seed");
        ARG(run, "NS-3 run number");
        ARG(payload, "Application payload bytes");
        ARG(queueCapacity, "Pending packets per node");
        ARG(maxHops, "Transmission hop limit");
        ARG(flows, "Default flow count");
        ARG(duration, "Simulation duration seconds");
        ARG(start, "Traffic start seconds");
        ARG(stop, "Traffic stop seconds");
        ARG(rate, "Packets per second per flow");
        ARG(spacing, "Line/grid spacing metres");
        ARG(area, "Random/waypoint square side metres");
        ARG(range, "Maximum radio range metres, also estimator hop scale");
        ARG(power, "Wi-Fi transmit power dBm");
        ARG(pathLoss, "Log-distance exponent");
        ARG(speed, "Mobility speed m/s");
        ARG(pause, "Waypoint pause seconds");
        ARG(processing, "Processing milliseconds");
        ARG(slowProcessing, "Diamond node 1 processing milliseconds");
        ARG(minHoldoff, "Minimum holdoff milliseconds");
        ARG(maxHoldoff, "Maximum holdoff milliseconds");
        ARG(safety, "Deadline safety margin milliseconds");
        ARG(perHop, "Predicted downstream milliseconds per hop");
        ARG(hello, "Beacon interval seconds");
        ARG(deadline, "Override all deadlines ms; zero uses classes");
        ARG(loss, "Explicit fault injection probability");
        ARG(lossNode, "Fault-injection receiver; UINT_MAX disables");
        ARG(diamondHeight, "Diamond half-height metres");
#undef ARG
        cmd.AddValue("weights", "Link,progress,slack,queue weights", weights);
        cmd.AddValue("mix", "Four class proportions", mix);
        cmd.AddValue("deadlines", "Four class deadlines ms", deadlines);
        cmd.AddValue("pairs", "Flow pairs source:dest separated by commas", pairs);
        cmd.AddValue("selfTest", "Run C++ tests", selfTest);
        cmd.Parse(argc, argv);
        if (selfTest)
        {
            SelfTest();
            return 0;
        }
        ParseArray(weights, c.weights);
        ParseArray(mix, c.mix);
        ParseArray(deadlines, c.deadlines);
        if (!pairs.empty())
        {
            std::stringstream s(pairs);
            std::string part;
            while (std::getline(s, part, ','))
            {
                auto colon = part.find(':');
                Require(colon != std::string::npos, "Invalid pair");
                c.pairs.emplace_back(std::stoul(part.substr(0, colon)),
                                     std::stoul(part.substr(colon + 1)));
            }
        }
        c.Validate();
        if (c.pairs.empty())
        {
            for (uint32_t f = 0; f < c.flows; f++)
            {
                c.pairs.emplace_back(f, c.nodes - 1);
            }
        }
        Require(!std::filesystem::exists(c.output) || std::filesystem::is_empty(c.output),
                "Output directory must be empty");
        RngSeedManager::SetSeed(c.seed);
        RngSeedManager::SetRun(c.run);
        NodeContainer nodes;
        nodes.Create(c.nodes);
        auto rng = CreateObject<UniformRandomVariable>();
        rng->SetStream(1);
        std::vector<Vector> initial;
        auto allocator = CreateObject<ListPositionAllocator>();
        uint32_t cols = std::ceil(std::sqrt(c.nodes));
        for (uint32_t i = 0; i < c.nodes; i++)
        {
            Vector p;
            if (c.topology == "diamond")
            {
                std::vector<Vector> diamond{{0, 50, 0},
                                            {90, 50 + c.diamondHeight, 0},
                                            {70, 50 - c.diamondHeight, 0},
                                            {160, 50, 0}};
                p = diamond[i];
            }
            else if (c.topology == "line")
            {
                p = Vector(i * c.spacing, 0, 0);
            }
            else if (c.topology == "grid")
            {
                p = Vector((i % cols) * c.spacing, (i / cols) * c.spacing, 0);
            }
            else
            {
                p = Vector(rng->GetValue(0, c.area), rng->GetValue(0, c.area), 0);
            }
            initial.push_back(p);
            allocator->Add(p);
        }
        MobilityHelper mobility;
        mobility.SetPositionAllocator(allocator);
        if (c.mobility == "waypoint")
        {
            auto randomPos = CreateObject<RandomRectanglePositionAllocator>();
            auto x = CreateObject<UniformRandomVariable>();
            auto y = CreateObject<UniformRandomVariable>();
            x->SetAttribute("Max", DoubleValue(c.area));
            y->SetAttribute("Max", DoubleValue(c.area));
            x->SetStream(2);
            y->SetStream(3);
            randomPos->SetX(x);
            randomPos->SetY(y);
            mobility.SetMobilityModel("ns3::RandomWaypointMobilityModel",
                                      "Speed",
                                      StringValue("ns3::ConstantRandomVariable[Constant=" +
                                                  std::to_string(std::max(c.speed, .001)) + "]"),
                                      "Pause",
                                      StringValue("ns3::ConstantRandomVariable[Constant=" +
                                                  std::to_string(c.pause) + "]"),
                                      "PositionAllocator",
                                      PointerValue(randomPos));
        }
        else
        {
            mobility.SetMobilityModel(c.mobility == "velocity"
                                          ? "ns3::ConstantVelocityMobilityModel"
                                          : "ns3::ConstantPositionMobilityModel");
        }
        mobility.Install(nodes);
        mobility.AssignStreams(nodes, 100);
        if (c.mobility == "velocity")
        {
            for (uint32_t i = 0; i < c.nodes; i++)
            {
                nodes.Get(i)->GetObject<ConstantVelocityMobilityModel>()->SetVelocity(
                    Vector(i % 2 ? c.speed : -c.speed, 0, 0));
            }
        }
        YansWifiChannelHelper channel;
        channel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel");
        channel.AddPropagationLoss("ns3::LogDistancePropagationLossModel",
                                   "Exponent",
                                   DoubleValue(c.pathLoss));
        channel.AddPropagationLoss("ns3::RangePropagationLossModel",
                                   "MaxRange",
                                   DoubleValue(c.range));
        YansWifiPhyHelper phy;
        phy.SetChannel(channel.Create());
        phy.Set("TxPowerStart", DoubleValue(c.power));
        phy.Set("TxPowerEnd", DoubleValue(c.power));
        phy.Set("ChannelSettings", StringValue("{36, 20, BAND_5GHZ, 0}"));
        WifiHelper wifi;
        wifi.SetStandard(WIFI_STANDARD_80211a);
        wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                     "DataMode",
                                     StringValue(c.rateMode),
                                     "ControlMode",
                                     StringValue("OfdmRate6Mbps"));
        ns3::Config::SetDefault("ns3::WifiRemoteStationManager::NonUnicastMode",
                                StringValue(c.rateMode));
        WifiMacHelper mac;
        mac.SetType("ns3::AdhocWifiMac");
        auto devices = wifi.Install(phy, mac, nodes);
        wifi.AssignStreams(devices, 1000);
        InternetStackHelper internet;
        internet.Install(nodes);
        Ipv4AddressHelper address;
        address.SetBase("10.1.0.0", "255.255.0.0");
        address.Assign(devices);
        // Offline BFS over initial range graph for fixed-next-hop only; never refreshed.
        std::vector<std::vector<uint32_t>> routes(c.nodes,
                                                  std::vector<uint32_t>(c.nodes, UINT32_MAX));
        for (uint32_t dest = 0; dest < c.nodes; dest++)
        {
            std::queue<uint32_t> q;
            q.push(dest);
            std::vector<bool> visited(c.nodes);
            visited[dest] = true;
            while (!q.empty())
            {
                auto u = q.front();
                q.pop();
                for (uint32_t v = 0; v < c.nodes; v++)
                {
                    if (!visited[v] && CalculateDistance(initial[u], initial[v]) <= c.range)
                    {
                        visited[v] = true;
                        routes[v][dest] = u;
                        q.push(v);
                    }
                }
            }
        }
        Trace trace(c.output);
        AnimationInterface animation(c.output + "/animation.xml");
        animation.EnablePacketMetadata();
        for (uint32_t i = 0; i < c.nodes; i++)
        {
            animation.UpdateNodeDescription(i, "Relay " + std::to_string(i));
            animation.UpdateNodeColor(i, 229, 160, 40);
            animation.UpdateNodeSize(i, 8, 8);
        }
        for (const auto& [source, destination] : c.pairs)
        {
            animation.UpdateNodeDescription(source, "Source " + std::to_string(source));
            animation.UpdateNodeColor(source, 59, 130, 246);
            animation.UpdateNodeDescription(destination, "Destination " + std::to_string(destination));
            animation.UpdateNodeColor(destination, 0, 201, 167);
        }
        std::vector<Ptr<Routing>> apps;
        for (uint32_t i = 0; i < c.nodes; i++)
        {
            auto app = CreateObject<Routing>();
            app->Setup(i, &c, &trace, initial, routes);
            nodes.Get(i)->AddApplication(app);
            app->SetStartTime(Seconds(0));
            app->SetStopTime(Seconds(c.duration));
            apps.push_back(app);
            auto dev = DynamicCast<WifiNetDevice>(devices.Get(i));
            dev->GetPhy()->TraceConnectWithoutContext("PhyTxBegin",
                                                      MakeBoundCallback(&PhyTx, &trace, i));
            dev->GetPhy()->TraceConnectWithoutContext("PhyRxDrop",
                                                      MakeBoundCallback(&PhyDrop, &trace, i));
        }
        for (uint32_t i = 0; i < c.pairs.size(); i++)
        {
            auto cls = CreateObject<UniformRandomVariable>();
            cls->SetStream(2000 + 2 * i);
            auto poisson = CreateObject<ExponentialRandomVariable>();
            poisson->SetAttribute("Mean", DoubleValue(1 / c.rate));
            poisson->SetStream(2001 + 2 * i);
            Simulator::Schedule(Seconds(c.start),
                                &Arrival,
                                apps[c.pairs[i].first],
                                c.pairs[i].second,
                                &c,
                                cls,
                                poisson);
        }
        Simulator::ScheduleNow(&Positions, nodes, &trace, c.duration);
        Simulator::Stop(Seconds(c.duration));
        Simulator::Run();
        Simulator::Destroy();
        std::cout << "NS-3.45 completed " << c.protocol << " with " << c.nodes
                  << " nodes; traces: " << c.output << '\n';
        return 0;
    }
    catch (const std::exception& e)
    {
        std::cerr << "Error: " << e.what() << '\n';
        return 2;
    }
}
