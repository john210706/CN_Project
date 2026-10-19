#pragma once
#include "model.h"
#include "packet-header.h"

#include "ns3/application.h"
#include "ns3/mobility-model.h"
#include "ns3/random-variable-stream.h"
#include "ns3/socket.h"

#include <deque>
#include <fstream>
#include <map>
#include <set>

namespace lab
{
struct Trace
{
    std::ofstream events, positions, summary, radio;
    explicit Trace(const std::string& path);
    void Event(const std::string& type,
               const Header& h,
               uint32_t node,
               const std::string& reason = "",
               const Decision& d = {});
};

class Routing : public ns3::Application
{
  public:
    void Setup(uint32_t id,
               const Config* c,
               Trace* trace,
               const std::vector<ns3::Vector>& initial,
               const std::vector<std::vector<uint32_t>>& routes);
    void Generate(uint32_t destination, uint8_t cls, double lifetime);
    static ns3::TypeId GetTypeId();

  private:
    struct Neighbor
    {
        uint32_t first = 0, last = 0;
        std::deque<std::pair<uint32_t, int64_t>> beacons;
        int64_t updated = 0;
    };

    struct State
    {
        ns3::EventId event, expiryEvent;
        Header h;
        int64_t retainUntil;
        bool pending = false, forwarded = false;
    };

    uint32_t id_ = 0, sequence_ = 0, beacon_ = 0;
    const Config* c_ = nullptr;
    Trace* t_ = nullptr;
    ns3::Ptr<ns3::Socket> socket_;
    ns3::Ptr<ns3::UniformRandomVariable> random_;
    std::vector<ns3::Vector> initial_;
    std::vector<std::vector<uint32_t>> routes_;
    std::map<uint64_t, State> states_;
    std::map<uint32_t, Neighbor> neighbors_;
    ns3::EventId helloEvent_, cleanEvent_;
    uint32_t pending_ = 0;
    double serviceFree_ = 0;
    void StartApplication() override;
    void StopApplication() override;
    void Hello();
    void Cleanup();
    void Receive(ns3::Ptr<ns3::Socket> socket);
    void Schedule(Header h, Decision d, bool origin = false);
    void Forward(uint64_t key);
    void Expire(uint64_t key);
    void Transmit(Header h);
    double Quality(uint32_t sender);
    double Processing() const;
};
} // namespace lab
