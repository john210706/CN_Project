# Deadline-Aware Opportunistic Routing for Wireless Networks
## Simulation-Based Study Using NS-3

### Abstract
This project studies whether receiver-side deadline feasibility can improve useful
packet delivery in an unreliable wireless network. Three C++ application-layer forwarding
strategies execute over the same NS-3.45 ad-hoc Wi-Fi/UDP transport: fixed next hop,
progress/link-based opportunistic forwarding, and deadline-aware opportunistic forwarding.
The proposed strategy combines normalized local link reception, geographic progress,
predicted slack and queue availability with cancellable forwarding timers. The accompanying
Python pipeline preserves packet-level evidence, independent-seed summaries and interactive
trace playback. Results below are read from successful simulation outputs; they are not
predictions or guarantees for deployed emergency communication.

### Introduction, problem and motivation
Packet delivery alone is insufficient when information loses value after a deadline.
An emergency message may arrive successfully yet too late to act upon. Wireless broadcast
also creates multiple possible relays, making the choice of which receiver forwards a
concrete opportunity to consider timeliness. The research question is whether using
remaining lifetime and estimated delivery delay improves deadline-satisfied delivery
relative to fixed and deadline-unaware forwarding under comparable conditions.

### Objectives
Implement real multi-hop wireless transmission, coordinate competing receivers, enforce
absolute packet deadlines, quantify delivery and overhead, and make every plotted outcome
traceable to actual simulator events. The hypothesis is conditional: deadline awareness
may help when candidate delays differ, but poor prediction can reject useful opportunities.

### Related work
Biswas and Morris's ExOR work selects relays after reception to exploit wireless diversity.
This project uses that broad receiver-opportunity idea, but does not reproduce ExOR's
batch coordination or MAC design. SPEED by He, Stankovic, Lu and Abdelzaher studies
soft real-time communication through geographic forwarding and delivery-speed control.
The present project's local slack score is an educational experimental design, not an
implementation of SPEED or a claim of a novel proven protocol. See the verified references.

### Architecture and implementation
The per-node C++ application owns a UDP socket, HELLO history, processing queue and packet
state. Every data hop traverses actual NS-3 Wi-Fi MAC/PHY models. A 76-byte serializable
header carries source/sequence identity, target, class, original creation/expiry, hop state
and positions. Python validates configurations, launches the compiled executable, derives
metrics from first destination arrival, aggregates seeds and renders figures. Streamlit
shows real topology samples, reception edges, candidate reasoning and outcomes.
See architecture.md for the network, lifecycle and pipeline diagrams.

### Proposed method
Let q be bounded HELLO reception quality, g normalized positive destination progress,
P local processing, Q reserved work and d distance to the initially configured target.
Predict D0=P+Q+ceil(d/range)*perHop. Normalize positive pre-contention slack and queue
availability, then score 0.3q+0.3g+0.3slack+0.1availability. Convert score to a bounded
holdoff and accept only when D0+holdoff+safety is strictly below remaining lifetime.
The node reserves a finite processing slot and schedules a forwarding event. It cancels
on an actual overheard downstream copy or expiry. It rechecks expiry immediately before
submitting to UDP. Basic opportunistic forwarding uses 0.5q+0.5g without deadline
eligibility. Fixed forwarding uses only the initial BFS next hop. Full equations and
state rules are in algorithm.md.

### Experimental setup and metrics
The radio is 802.11a at 5 GHz, 20 MHz, normally 6 Mbps and 30 dBm, with log-distance
attenuation and a 125 m maximum range. The primary design varies deadlines, offered
load, node density in a fixed square, path-loss exponent and waypoint motion separately.
All protocols share exogenous topology, traffic and mobility settings. Radio outcomes
need not remain paired because forwarding changes contention. Each primary scenario
uses five independent seeds. PDR counts unique deliveries, DSDR unique on-time deliveries,
and delay includes delivered packets only. Throughput counts delivered payload over full
simulation duration. Student-t 95% intervals use per-run outcomes, with sample size shown.
See methodology.md and metrics.md for definitions and censoring considerations.

### Measured results
This report includes **300 successful runs**, **20 named scenarios**, and **2 batches**.

| scenario | protocol | dsdr_pct_mean | dsdr_pct_ci95 | dsdr_pct_n | pdr_pct_mean | mean_delay_ms_mean | forwarding_transmissions_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| channel-2_6 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 4.00 | 102.00 |
| channel-2_6 | fixed | 100.00 | 0.00 | 5 | 100.00 | 3.17 | 34.00 |
| channel-2_6 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 4.14 | 34.00 |
| channel-3_0 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 4.00 | 102.00 |
| channel-3_0 | fixed | 100.00 | 0.00 | 5 | 100.00 | 3.17 | 34.00 |
| channel-3_0 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 4.14 | 34.00 |
| channel-3_8 | deadline_aware | 0.00 | 0.00 | 5 | 0.00 | — | 0.00 |
| channel-3_8 | fixed | 0.00 | 0.00 | 5 | 0.00 | — | 0.00 |
| channel-3_8 | opportunistic | 0.00 | 0.00 | 5 | 0.00 | — | 0.00 |
| deadline-100 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 4.05 | 510.00 |
| deadline-100 | fixed | 100.00 | 0.00 | 5 | 100.00 | 3.17 | 170.00 |
| deadline-100 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 4.22 | 204.00 |
| deadline-200 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 4.02 | 510.00 |
| deadline-200 | fixed | 100.00 | 0.00 | 5 | 100.00 | 3.17 | 170.00 |
| deadline-200 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 4.22 | 204.00 |
| deadline-300 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 4.01 | 510.00 |
| deadline-300 | fixed | 100.00 | 0.00 | 5 | 100.00 | 3.17 | 170.00 |
| deadline-300 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 4.22 | 204.00 |
| deadline-50 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 4.12 | 510.00 |
| deadline-50 | fixed | 100.00 | 0.00 | 5 | 100.00 | 3.17 | 170.00 |
| deadline-50 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 4.22 | 204.00 |
| deadline-500 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 4.00 | 510.00 |
| deadline-500 | fixed | 100.00 | 0.00 | 5 | 100.00 | 3.17 | 170.00 |
| deadline-500 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 4.22 | 204.00 |
| density-10 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 2.64 | 54.40 |
| density-10 | fixed | 100.00 | 0.00 | 5 | 100.00 | 2.22 | 13.60 |
| density-10 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 2.75 | 40.80 |
| density-20 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 2.97 | 176.80 |
| density-20 | fixed | 100.00 | 0.00 | 5 | 100.00 | 2.54 | 20.40 |
| density-20 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 3.01 | 108.80 |
| density-30 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 2.81 | 282.20 |
| density-30 | fixed | 100.00 | 0.00 | 5 | 100.00 | 2.22 | 13.60 |
| density-30 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 2.94 | 201.60 |
| load-100 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 8.86 | 586.80 |
| load-100 | fixed | 100.00 | 0.00 | 5 | 100.00 | 7.17 | 170.00 |
| load-100 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 8.14 | 170.00 |
| load-20 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 8.02 | 102.00 |
| load-20 | fixed | 100.00 | 0.00 | 5 | 100.00 | 7.17 | 34.00 |
| load-20 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 8.14 | 34.00 |
| load-500 | deadline_aware | 62.40 | 1.17 | 5 | 62.40 | 34.04 | 1489.40 |
| load-500 | fixed | 65.15 | 0.12 | 5 | 65.15 | 27.44 | 556.00 |
| load-500 | opportunistic | 63.36 | 0.68 | 5 | 63.36 | 35.05 | 1345.40 |
| mobility-0 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 2.97 | 176.80 |
| mobility-0 | fixed | 100.00 | 0.00 | 5 | 100.00 | 2.54 | 20.40 |
| mobility-0 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 3.01 | 108.80 |
| mobility-15 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 3.07 | 206.00 |
| mobility-15 | fixed | 75.29 | 53.77 | 5 | 75.29 | 2.38 | 12.00 |
| mobility-15 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 3.19 | 134.20 |
| mobility-5 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 2.97 | 185.80 |
| mobility-5 | fixed | 90.59 | 26.13 | 5 | 90.59 | 2.54 | 17.20 |
| mobility-5 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 3.02 | 109.20 |
| density-50 | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 2.81 | 330.00 |
| density-50 | fixed | 90.00 | 27.76 | 5 | 90.00 | 2.22 | 10.20 |
| density-50 | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 2.67 | 189.80 |
| weights-link | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 3.87 | 142.80 |
| weights-link | fixed | 100.00 | 0.00 | 5 | 100.00 | 3.17 | 34.00 |
| weights-link | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 4.14 | 34.00 |
| weights-slack | deadline_aware | 100.00 | 0.00 | 5 | 100.00 | 3.94 | 127.60 |
| weights-slack | fixed | 100.00 | 0.00 | 5 | 100.00 | 3.17 | 34.00 |
| weights-slack | opportunistic | 100.00 | 0.00 | 5 | 100.00 | 4.14 | 34.00 |

### Differences against baselines

Positive differences favor the proposed method; negative values are retained.

| scenario | baseline | dsdr_difference_pp | dsdr_relative_change_pct |
| --- | --- | --- | --- |
| channel-2_6 | fixed | 0.00 | 0.00 |
| channel-2_6 | opportunistic | 0.00 | 0.00 |
| channel-3_0 | fixed | 0.00 | 0.00 |
| channel-3_0 | opportunistic | 0.00 | 0.00 |
| channel-3_8 | fixed | 0.00 | — |
| channel-3_8 | opportunistic | 0.00 | — |
| deadline-100 | fixed | 0.00 | 0.00 |
| deadline-100 | opportunistic | 0.00 | 0.00 |
| deadline-200 | fixed | 0.00 | 0.00 |
| deadline-200 | opportunistic | 0.00 | 0.00 |
| deadline-300 | fixed | 0.00 | 0.00 |
| deadline-300 | opportunistic | 0.00 | 0.00 |
| deadline-50 | fixed | 0.00 | 0.00 |
| deadline-50 | opportunistic | 0.00 | 0.00 |
| deadline-500 | fixed | 0.00 | 0.00 |
| deadline-500 | opportunistic | 0.00 | 0.00 |
| density-10 | fixed | 0.00 | 0.00 |
| density-10 | opportunistic | 0.00 | 0.00 |
| density-20 | fixed | 0.00 | 0.00 |
| density-20 | opportunistic | 0.00 | 0.00 |
| density-30 | fixed | 0.00 | 0.00 |
| density-30 | opportunistic | 0.00 | 0.00 |
| load-100 | fixed | 0.00 | 0.00 |
| load-100 | opportunistic | 0.00 | 0.00 |
| load-20 | fixed | 0.00 | 0.00 |
| load-20 | opportunistic | 0.00 | 0.00 |
| load-500 | fixed | -2.75 | -4.23 |
| load-500 | opportunistic | -0.96 | -1.52 |
| mobility-0 | fixed | 0.00 | 0.00 |
| mobility-0 | opportunistic | 0.00 | 0.00 |
| mobility-15 | fixed | 24.71 | 32.81 |
| mobility-15 | opportunistic | 0.00 | 0.00 |
| mobility-5 | fixed | 9.41 | 10.39 |
| mobility-5 | opportunistic | 0.00 | 0.00 |
| density-50 | fixed | 10.00 | 11.11 |
| density-50 | opportunistic | 0.00 | 0.00 |
| weights-link | fixed | 0.00 | 0.00 |
| weights-link | opportunistic | 0.00 | 0.00 |
| weights-slack | fixed | 0.00 | 0.00 |
| weights-slack | opportunistic | 0.00 | 0.00 |

Against fixed, the proposed method has a higher observed mean in 3 scenario/batch comparisons, a lower mean in 1, and an equal mean in 16. These counts are descriptive, not significance tests.

Against opportunistic, the proposed method has a higher observed mean in 0 scenario/batch comparisons, a lower mean in 1, and an equal mean in 19. These counts are descriptive, not significance tests.

### Source provenance and figures

- Batch `20261019T192805_cab57b`: 255 runs. [Run manifest](../results/raw/20261019T192805_cab57b/analysis/runs.csv), [aggregate table](../results/raw/20261019T192805_cab57b/analysis/aggregate.csv).

![Measured load-500_dsdr_pct.svg](../results/raw/20261019T192805_cab57b/analysis/figures/load-500_dsdr_pct.svg)

![Measured sensitivity_deadline.svg](../results/raw/20261019T192805_cab57b/analysis/figures/sensitivity_deadline.svg)

![Measured sensitivity_rate.svg](../results/raw/20261019T192805_cab57b/analysis/figures/sensitivity_rate.svg)

![Measured sensitivity_nodes.svg](../results/raw/20261019T192805_cab57b/analysis/figures/sensitivity_nodes.svg)

![Measured sensitivity_pathLoss.svg](../results/raw/20261019T192805_cab57b/analysis/figures/sensitivity_pathLoss.svg)

![Measured sensitivity_speed.svg](../results/raw/20261019T192805_cab57b/analysis/figures/sensitivity_speed.svg)
- Batch `20261019T192957_45fe78`: 45 runs. [Run manifest](../results/raw/20261019T192957_45fe78/analysis/runs.csv), [aggregate table](../results/raw/20261019T192957_45fe78/analysis/aggregate.csv).

![Measured sensitivity_nodes.svg](../results/raw/20261019T192957_45fe78/analysis/figures/sensitivity_nodes.svg)

### Discussion
A higher DSDR accompanied by lower PDR can reflect deliberate rejection of predicted
late packets. Lower delivered-only delay may partly reflect this selection. Extra relays
increase overhead even when they deliver useful packets. Low-loss, lightly loaded cases
can leave little room for improvement. Dense networks can improve reception diversity
but also create more contention and hidden-terminal competition. Weak channels or stale
locations can disconnect the available greedy paths. No zero-delivery run is removed.

### Limitations and future work
The baseline is application-level fixed forwarding over broadcast, not AODV/OLSR. Target
locations are initially configured and can become stale. Greedy progress has no void
recovery. The downstream predictor is approximate; HELLOs are smaller than data packets.
Cancellation does not reclaim committed processing work or remove packets already queued
inside Wi-Fi. Hidden receivers cannot suppress one another reliably. Short five-seed
replications are insufficient for deployment or universal significance claims. Future
work should compare adaptive delay estimators, refreshed location announcements,
longer experiments, realistic obstacles/fading, and an additional standard IP-routing baseline.

### Conclusion
The artifact provides an executable experimental test of deadline-aware receiver selection
and a reproducible route from Wi-Fi events to measured metrics, plots and inspection.
The observed results apply to the recorded scenarios and modeling assumptions. They do
not establish that deadline-aware forwarding always wins or guarantees emergency delivery.

### References
1. NS-3.45 official installation guide: https://www.nsnam.org/docs/release/3.45/installation/html/overview.html
2. NS-3.45 official source mirror: https://github.com/nsnam/ns-3-dev-git/tree/ns-3.45
3. S. Biswas and R. Morris, ExOR: Opportunistic Multi-Hop Routing for Wireless Networks,
   ACM SIGCOMM 2005. Official program: https://conferences.sigcomm.org/sigcomm/2005/techprog.html
4. T. He, J. Stankovic, C. Lu and T. Abdelzaher, SPEED: A Stateless Protocol for Real-Time
   Communication in Sensor Networks, ICDCS 2003. Author publication record:
   https://www.cs.virginia.edu/~stankovic/sensornet.html

### Data loading warnings

0 failed/unavailable records found.
