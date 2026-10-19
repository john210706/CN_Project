#include "packet-header.h"

namespace lab
{
NS_OBJECT_ENSURE_REGISTERED(Header);

ns3::TypeId
Header::GetTypeId()
{
    static ns3::TypeId t =
        ns3::TypeId("lab::Header").SetParent<ns3::Header>().AddConstructor<Header>();
    return t;
}

ns3::TypeId
Header::GetInstanceTypeId() const
{
    return GetTypeId();
}

void
Header::Serialize(ns3::Buffer::Iterator i) const
{
    i.WriteU8(version);
    i.WriteU8(kind);
    i.WriteU8(trafficClass);
    i.WriteU8(reserved);
    for (auto v : {source, destination, sequence, last, next})
    {
        i.WriteHtonU32(v);
    }
    i.WriteHtonU64(created);
    i.WriteHtonU64(expiry);
    i.WriteHtonU16(hops);
    i.WriteHtonU16(limit);
    for (auto v : {x, y, dx, dy})
    {
        i.WriteHtonU32(static_cast<uint32_t>(v));
    }
    for (auto v : {queue, processingUs, beacon, payload})
    {
        i.WriteHtonU32(v);
    }
}

uint32_t
Header::Deserialize(ns3::Buffer::Iterator i)
{
    if (i.GetRemainingSize() < GetSerializedSize())
    {
        version = 0;
        return 0;
    }
    version = i.ReadU8();
    kind = i.ReadU8();
    trafficClass = i.ReadU8();
    reserved = i.ReadU8();
    source = i.ReadNtohU32();
    destination = i.ReadNtohU32();
    sequence = i.ReadNtohU32();
    last = i.ReadNtohU32();
    next = i.ReadNtohU32();
    created = i.ReadNtohU64();
    expiry = i.ReadNtohU64();
    hops = i.ReadNtohU16();
    limit = i.ReadNtohU16();
    x = static_cast<int32_t>(i.ReadNtohU32());
    y = static_cast<int32_t>(i.ReadNtohU32());
    dx = static_cast<int32_t>(i.ReadNtohU32());
    dy = static_cast<int32_t>(i.ReadNtohU32());
    queue = i.ReadNtohU32();
    processingUs = i.ReadNtohU32();
    beacon = i.ReadNtohU32();
    payload = i.ReadNtohU32();
    return GetSerializedSize();
}

bool
Header::Valid(uint32_t n) const
{
    return version == 1 && kind <= 1 && source < n && last < n &&
           (kind == 1 ||
            (destination < n && source != destination && trafficClass < 4 && expiry > created &&
             limit > 0 && hops <= limit && (next == UINT32_MAX || next < n)));
}

void
Header::Print(std::ostream& o) const
{
    o << "id=" << Id() << " hops=" << hops << " expires_ns=" << expiry;
}
} // namespace lab
