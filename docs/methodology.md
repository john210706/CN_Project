# Experimental methodology

The implementation targets NS-3.45, C++20 as selected by upstream, Linux and Python 3.12.
Wi-Fi is IEEE 802.11a at 5 GHz, 20 MHz, constant 6 Mbps by default. Both broadcast
and unicast rate configuration are explicit. UDP broadcast has no per-receiver MAC ACK
or retry. Yans models propagation delay, path loss, receiver interference, contention
and packet error behavior. LogDistance exponent defaults to 3; RangePropagationLoss
imposes a documented 125 m cutoff. Transmit power is 30 dBm. Rate and power are configurable;
this release fixes channel width at 20 MHz rather than accepting invalid width/rate pairs.

Static line spacing is 80 m; grid uses ceil(sqrt(N)) columns. The four-node diamond
places A=(0,50), B=(90,70), C=(70,30), Z=(160,50) metres. `diamondHeight` changes
the half-height, allowing B and C to be hidden from one another. Random topology uses
an independent seeded position stream in a square. Density experiments fix the square
at 250×250 m while changing N. There is no connectivity guarantee or resampling of
unfavorable layouts. Static nodes, true random-waypoint and constant-velocity mobility
are implemented. Waypoint is bounded; velocity intentionally continues without boundary
reflection, so it can demonstrate disconnection. Destination coordinates are initially
provisioned and not refreshed. No store-and-carry recovery is implemented.

Constant-rate traffic begins after HELLO warmup. Poisson traffic has independent
exponential interarrival streams. Classes use a separate stream per flow. Source IDs
plus sequence numbers avoid multi-flow collisions. All three modes use the same payload,
header, HELLO interval, topology, motion, traffic streams, seed and run setting.
The fixed mode has an initial geometric BFS route and keeps it despite motion or loss.
This is a simple fixed-next-hop baseline, not a comparison against AODV or OLSR.

Different forwarding behavior changes contention and RNG consumption inside Wi-Fi.
Aligned exogenous streams are **not** identical per-packet channel realizations.
The optional `loss` / `lossNode` receiver fault injection is separately logged and disabled
in primary experiments. No measured link quality is hardcoded to favor a protocol.

The primary matrix executes 17 individual scenarios, three protocols and five seeds
(255 runs). Warmup is 0.8 s, traffic ends at 2.5 s, and simulation stops at 4 s.
This is a short reproducible study; steady-state claims require longer replications.
Per-run DSDR, PDR, delay and overhead are aggregated across seeds using sample standard
deviation and a two-sided Student-t 95% interval. One usable sample has no interval.
Unbounded t intervals are not truncated to [0,100] in the data; they are approximations
for bounded ratios. Delay means can exclude seeds with no delivered packets; `*_n`
reports the effective sample count. Packet outcomes within a run are correlated and
are not treated as independent statistical replicates. ECDFs pool delivered packets
within each named scenario for descriptive visualization, not significance testing.

Percentage-point difference is proposed DSDR minus baseline DSDR. Relative change divides
that difference by the baseline and is undefined for zero. Missing or failed runs stay
visible in the failure ledger. A five-seed average is evidence within this model, not
proof of performance in deployed emergency networks.
