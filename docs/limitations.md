# Known modeling limits

- This is a simulator study, not a deployment or hard real-time guarantee.
- All modes are application-layer forwarding over UDP broadcast. The fixed baseline
  has no MAC ACK/retry advantage, dynamic route discovery or AODV/OLSR repair.
- Initial geometric routes may include weak radio links; no successful-link oracle is used.
- Geographic progress can stall at voids; no perimeter recovery or delay-tolerant carry exists.
- Destination positions are configured initially, and become stale under mobility.
- The downstream estimate uses distance/hop scale and a constant per-hop prediction;
  it does not know future interference, queues, ACK outcomes or routes.
- HELLO success estimates incoming reception, with a short finite window. HELLOs are
  shorter than data, so their reception probability can differ.
- The diamond's per-node processing asymmetry is intentional experimental configuration,
  not a claim that a particular real device is slower. Controlled injected loss is optional
  and separately labeled; normal experiments use actual propagation and PHY errors.
- Suppression requires hearing a higher-depth copy. Hidden terminals and collisions
  leave real duplicates; there is no perfect distributed winner election.
- Committed processing reservations are not reclaimed when a timer is cancelled.
- App deadline checks cannot remove already submitted packets from the Wi-Fi MAC queue.
- Velocity mobility is unbounded; random-waypoint uses configured square boundaries.
- The maximum-range cutoff simplifies connectivity. Log-distance propagation has no
  obstacles, terrain, fading or interference from unrelated networks.
- IEEE 802.11a channel width is fixed at 20 MHz. Energy use and adaptive rates are outside scope.
- Fixed protocol can deliver late; the proposed policy intentionally drops predicted misses.
  Lower mean delay can therefore reflect delivery selection as well as faster forwarding.
- Short replications and five seeds do not establish steady state or statistical significance
  for arbitrary environments. Wide intervals and zero delivery are legitimate outputs.
- Packet trace logs and animation use full run files in memory; high-volume studies may
  require partitioned storage. Playback samples positions every 100 ms.
