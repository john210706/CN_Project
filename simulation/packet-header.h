#pragma once
#include "ns3/header.h"

#include <cstdint>

namespace lab
{
// All integers use network byte order; time is ns and coordinates are signed mm.
class Header : public ns3::Header
{
  public:
    static ns3::TypeId GetTypeId();
    ns3::TypeId GetInstanceTypeId() const override;

    uint32_t GetSerializedSize() const override
    {
        return 76;
    }

    void Serialize(ns3::Buffer::Iterator i) const override;
    uint32_t Deserialize(ns3::Buffer::Iterator i) override;
    void Print(std::ostream& os) const override;
    bool Valid(uint32_t nodes) const;

    uint64_t Id() const
    {
        return (uint64_t(source) << 32) | sequence;
    }

    uint8_t version = 1, kind = 0, trafficClass = 0, reserved = 0;
    uint32_t source = 0, destination = 0, sequence = 0, last = 0, next = UINT32_MAX;
    uint64_t created = 0, expiry = 0;
    uint16_t hops = 0, limit = 32;
    int32_t x = 0, y = 0, dx = 0, dy = 0;
    uint32_t queue = 0, processingUs = 0, beacon = 0, payload = 256;
};
} // namespace lab
