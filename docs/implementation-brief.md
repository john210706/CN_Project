# MASTER CODEX IMPLEMENTATION PROMPT

## PROJECT: Deadline-Aware Opportunistic Routing for Wireless Networks

### Your Role

You are an expert computer networks researcher, senior C++ engineer, NS-3 simulation developer, routing protocol designer, Python data engineer, visualization developer, software architect, and quality-assurance engineer.

You are working on a serious undergraduate Computer Networks project titled:

**Deadline-Aware Opportunistic Routing for Wireless Networks — Simulation-Based Study Using NS-3**

Your responsibility is to design, implement, integrate, test, debug, validate, document, and deliver the complete project.

This is NOT a request for:
- A proof of concept.
- A basic tutorial.
- A toy simulation.
- A partial implementation.
- A skeleton containing TODO comments.
- A collection of disconnected scripts.
- A dashboard that displays fabricated data.
- A proposed architecture without functioning software.

I want a complete, maintainable, reproducible, academically defensible, working implementation.

Use your full reasoning and engineering capabilities. Make sound technical decisions and verify them by building and executing the project.

**Do not stop after providing a plan. Begin creating and implementing the actual files in the current workspace.**

Do not ask routine design questions. Make reasonable engineering decisions, document them, and proceed. Ask only if a genuine blocker requires information that cannot reasonably be inferred.

Work incrementally, verify each subsystem, fix errors, and continue until the acceptance criteria are satisfied or an external limitation prevents further execution.

---

# 1. PROJECT BACKGROUND AND OBJECTIVE

## 1.1 Background

Wireless networks are used for applications such as:

- Emergency communications.
- Vehicular ad-hoc networks.
- Disaster-response networks.
- Industrial IoT.
- Wireless sensor networks.
- Real-time multimedia.
- Time-sensitive data transmission.

Wireless communication can be unreliable due to interference, packet loss, mobility, congestion, and changing channel conditions.

Traditional fixed-next-hop routing relies on a predetermined forwarding decision. When the chosen wireless link performs poorly, packet delivery may fail or experience increased delay.

Opportunistic routing exploits wireless broadcast: multiple neighbouring nodes may receive a transmitted packet, and an eligible receiver can become the next forwarder.

However, packet delivery alone does not guarantee usefulness.

For a time-sensitive application, a packet arriving after its deadline may have little or no value.

## 1.2 Core Problem

Consider an emergency warning that must reach its destination within 50 milliseconds.

Node A broadcasts it, and Nodes B and C receive it.

Node B:
- Link quality: 95%.
- Estimated remaining delivery delay: 80 ms.

Node C:
- Link quality: 85%.
- Estimated remaining delivery delay: 20 ms.

Remaining packet lifetime: 50 ms.

A routing decision based mainly on link quality may prefer B.

The proposed algorithm should recognize that B is unlikely to meet the deadline, while C has a better estimated chance of delivering the packet on time.

The objective is not merely to maximize received packets.

**The objective is to maximize successfully delivered packets that arrive before their deadlines, while controlling forwarding overhead, duplicate transmissions, delay, and packet loss.**

## 1.3 Primary Research Question

Does deadline-aware opportunistic forwarding improve the deadline-satisfied delivery ratio compared with conventional fixed-next-hop forwarding and basic deadline-unaware opportunistic forwarding under varying network conditions?

## 1.4 Research Hypothesis

Considering remaining packet lifetime and estimated downstream delivery delay when selecting forwarding candidates may improve timely packet delivery, particularly under congestion, unreliable wireless links, and mobility.

This is a hypothesis to test, not an outcome to assume.

Do not manipulate experiments or fabricate results to guarantee that the proposed protocol wins.

---

# 2. REQUIRED TECHNOLOGY STACK

Use the following stack unless technical compatibility requires a justified alternative.

## Core simulator

- NS-3 network simulator.
- C++17 or the C++ standard supported by the selected NS-3 release.
- Real NS-3 Wi-Fi models.
- NS-3 networking, mobility, propagation, scheduling, and tracing APIs.
- CMake-based NS-3 build workflow.

Prefer a pinned stable NS-3 release, such as ns-3.45, after verifying compatibility. If a more appropriate stable release is already installed, inspect it and document the chosen version.

Do not blindly copy API calls from tutorials written for obsolete NS-3 versions.

Use official documentation:

- https://www.nsnam.org/
- https://www.nsnam.org/docs/
- https://gitlab.com/nsnam/ns-3-dev

## Analysis

- Python 3.
- pandas.
- NumPy.
- Matplotlib.
- Seaborn only if helpful for statistical plotting.
- SciPy where appropriate.
- Plotly for interactive charts.

## Interactive visualization

Prefer:

- Streamlit.
- Plotly.

The dashboard must be a genuine companion to the NS-3 simulation, not an alternative simulator.

## Development

- Git.
- pytest.
- C++ unit/integration tests as appropriate.
- Shell scripts or Python-based launchers.
- YAML or JSON configuration.
- CSV and JSON result exports.

## Supported environment

Target Linux, preferably Ubuntu or Ubuntu under WSL2.

Inspect the actual execution environment before choosing installation commands.

If running in a non-Linux environment, use a supported approach and document differences.

Do not assume dependencies are installed.

Avoid unnecessary dependencies and unnecessary duplication of the entire NS-3 source tree.

---

# 3. PROJECT ARCHITECTURE

Design the implementation using a clean modular architecture.

The exact structure may change to accommodate verified NS-3 build conventions, but aim for something similar to:

```text
deadline-aware-opportunistic-routing/
│
├── README.md
├── LICENSE
├── .gitignore
├── Makefile
├── requirements.txt
├── pyproject.toml
│
├── config/
│   ├── default.yaml
│   ├── diamond.yaml
│   ├── static-grid.yaml
│   ├── mobile-network.yaml
│   ├── high-loss.yaml
│   ├── congestion.yaml
│   └── experiment-matrix.yaml
│
├── simulation/
│   ├── main.cc
│   ├── packet-header.h
│   ├── packet-header.cc
│   ├── routing-application.h
│   ├── routing-application.cc
│   ├── routing-strategies.h
│   ├── routing-strategies.cc
│   ├── candidate-selector.h
│   ├── candidate-selector.cc
│   ├── neighbor-table.h
│   ├── neighbor-table.cc
│   ├── traffic-generator.h
│   ├── traffic-generator.cc
│   ├── metrics-collector.h
│   ├── metrics-collector.cc
│   ├── trace-writer.h
│   ├── trace-writer.cc
│   └── CMakeLists.txt
│
├── scripts/
│   ├── setup.sh
│   ├── build.sh
│   ├── run_simulation.py
│   ├── run_experiments.py
│   ├── validate_results.py
│   ├── generate_report.py
│   └── launch_dashboard.sh
│
├── analysis/
│   ├── load_results.py
│   ├── metrics.py
│   ├── aggregate.py
│   ├── statistics.py
│   └── plots.py
│
├── dashboard/
│   ├── app.py
│   ├── components/
│   ├── pages/
│   └── assets/
│
├── tests/
│   ├── test_packet_header.py
│   ├── test_deadline_logic.py
│   ├── test_metrics.py
│   ├── test_config.py
│   ├── test_cli.py
│   ├── test_smoke.py
│   ├── test_routing_integration.py
│   ├── test_duplicate_suppression.py
│   └── test_reproducibility.py
│
├── docs/
│   ├── architecture.md
│   ├── algorithm.md
│   ├── methodology.md
│   ├── experiment-design.md
│   ├── metrics.md
│   ├── implementation.md
│   ├── testing.md
│   ├── limitations.md
│   ├── presentation-guide.md
│   ├── viva-questions.md
│   └── final-report.md
│
├── results/
│   ├── raw/
│   ├── processed/
│   ├── figures/
│   └── reports/
│
└── evidence/
    └── validation.md
```

This is a logical architecture, not an instruction to manufacture empty files.

Every implemented component must have a purpose.

NS-3's actual CMake/scratch conventions take priority over this suggested layout.

One acceptable integration approach is to maintain the simulation sources in this repository and use a setup script to integrate a multi-file program with NS-3's scratch directory.

Verify the correct build target and source linkage rather than assuming an executable name.

Keep project code separate from unmodified NS-3 upstream code where practical.

Never overwrite an existing user's repository or unrelated work.

---

# 4. IMPLEMENT THE REAL NS-3 WIRELESS NETWORK

This is mandatory.

Do not build a Python-only approximation and describe it as an NS-3 simulation.

## 4.1 Node creation

Implement configurable network sizes:

- 4-node verification topology.
- 10 nodes.
- 20 nodes.
- 30 nodes.
- 50 nodes where computationally practical.

Support custom node counts through command-line arguments.

Each node must have:

- A unique ID.
- A configured position.
- An actual NS-3 wireless network device.
- A protocol stack appropriate to the implementation.
- A packet transmission and reception mechanism.
- Routing/application state.
- Access to the configured forwarding strategy.

## 4.2 Wireless communication

Use a real NS-3 ad-hoc Wi-Fi setup.

Simulate:

- Wireless broadcasting.
- Transmitter and receiver behavior.
- Wireless propagation loss.
- Medium contention.
- Interference.
- Packet reception failures.
- Data transmission time.
- Traffic-dependent delays.

Start with a reliable, documented Wi-Fi configuration.

Make transmission power, propagation settings, bandwidth, and data rate configurable where supported.

Avoid choosing default values that make all nodes hear all transmissions regardless of topology.

Do not simulate a radio link by directly calling a receiving node's application callback. Packets must pass through the NS-3 networking model.

## 4.3 Propagation and packet loss

Support documented channel conditions such as:

- Normal operating conditions.
- Increased path loss.
- Interference/congestion conditions.
- Unreliable links.
- Moving nodes.

Use NS-3 propagation and Wi-Fi models to produce realistic reception behavior.

An optional explicit fault-injection mechanism may be added for controlled loss experiments, but it must be clearly separated from actual radio-model packet loss.

Do not silently replace the radio model with arbitrary random packet dropping.

## 4.4 Node mobility

Support:

1. Static nodes.
2. Random waypoint mobility.
3. Configurable constant-velocity movement.
4. Optional structured vehicular movement.

Position and speed must affect actual NS-3 wireless connectivity.

The program must not merely animate node movement without updating the simulator's mobility model.

Support configurable movement boundaries, speeds, and pause times.

---

# 5. REQUIRED NETWORK TOPOLOGIES

Implement several repeatable topology generators.

## 5.1 Diamond topology

Create the following topology:

```text
        B
       / \
      /   \
     A     Z
      \   /
       \ /
        C
```

A = source.

Z = destination.

B and C = forwarding candidates.

The initial geometry must allow the project to demonstrate the reception of a packet by multiple candidates.

The simulation should allow controlled differences in:

- Candidate link reliability.
- Candidate processing delay.
- Candidate queue occupancy.
- Candidate distance to destination.
- Estimated delivery time.

This will be the primary algorithm demonstration.

## 5.2 Linear topology

```text
A --- B --- C --- D --- Z
```

Use it to verify real multi-hop packet delivery.

## 5.3 Grid topology

Place nodes in a configurable grid and allow packets to travel across multiple wireless hops.

## 5.4 Random topology

Generate reproducible random node positions.

Use configurable:

- Node count.
- Network area.
- Density.
- Random seed.

## 5.5 Mobile topology

Allow mobility to change available forwarding opportunities over time.

Document how temporary disconnections are handled.

---

# 6. PACKET DESIGN AND METADATA

Implement a real serializable packet header or equivalent network-transmitted metadata mechanism in C++.

Do not rely only on a simulator-side map of packet IDs while pretending that packet fields were transmitted.

Include at least:

- Header version.
- Unique packet identifier.
- Source node ID.
- Destination node ID.
- Sequence number.
- Traffic class.
- Packet creation timestamp.
- Absolute expiry timestamp or an unambiguous relative lifetime.
- Hop count.
- Hop limit.
- Last forwarding node ID.
- Any additional protocol-specific forwarding information needed.

Use clearly defined units and serialization rules.

Avoid floating-point timestamps in the transmitted header when integer timestamp representations are more reliable.

Implement and test:

- GetSerializedSize.
- Serialize.
- Deserialize.
- Print.
- Packet-header validity checks.

Make it possible to trace a packet by its unique identity across all hops.

Use a compound packet identity if necessary, such as:

```text
(source_id, sequence_number)
```

Packet IDs must not collide between different sources in the same simulation.

The three protocols must use equivalent traffic payloads and account for protocol-header overhead consistently.

---

# 7. TRAFFIC GENERATION SYSTEM

Implement an actual configurable traffic generator.

## 7.1 Packet classes

Support the following defaults:

| Traffic class | Deadline |
|---|---|
| Emergency | 50 ms |
| Video | 100 ms |
| Normal Data | 500 ms |
| Background | 1000 ms |

These are experiment defaults, not universal networking standards.

Support custom deadlines, including the 50–500 ms range described in the project abstract.

## 7.2 Traffic settings

Allow configuration of:

- Packet generation rate.
- Packet payload size.
- Simulation duration.
- Source nodes.
- Destination nodes.
- Number of simultaneous flows.
- Traffic-class proportions.
- Per-class deadlines.
- Start/stop times.
- Seed/run values.

Support a constant-rate source initially.

Add another reproducible traffic model, such as Poisson arrivals, when the core implementation is stable.

## 7.3 Multiple traffic flows

Support multiple active source-destination pairs.

Ensure packet IDs remain unique.

Track statistics both globally and per flow.

The source and destination must be distinguishable from intermediate forwarding nodes.

---

# 8. IMPLEMENT THREE REAL FORWARDING PROTOCOLS

The comparison must use three implemented forwarding behaviors.

A dashboard selector must not merely rename the same algorithm.

Use these protocol identifiers:

```text
fixed
opportunistic
deadline_aware
```

## 8.1 Protocol A: Fixed-Next-Hop Routing

Implement a conventional single-next-hop forwarding baseline.

Requirements:

- Each forwarding node has a selected next hop.
- The next-hop selection is established using a documented route or forwarding-table construction method.
- Only the designated next-hop node is permitted to forward a given transmission.
- A packet is not opportunistically handed to another receiver simply because that receiver overhears it.
- Routing decisions do not consider packet deadlines.
- Multi-hop forwarding works.
- Forwarding loops are prevented through hop limits and route checks.
- Failed or outdated forwarding paths are handled using a documented rule.

For methodological consistency, an application-layer fixed-next-hop forwarding baseline over the same NS-3 Wi-Fi/UDP broadcast transport as the other two modes is acceptable.

If this approach is selected, clearly label the baseline as **fixed-next-hop forwarding**, not AODV or an IP-layer routing protocol.

An AODV or OLSR comparison may be added separately, but do not misrepresent the baseline.

## 8.2 Protocol B: Basic Opportunistic Routing

Implement true opportunistic receiver-based forwarding.

Requirements:

- A sender broadcasts a packet.
- Several neighbouring nodes may successfully receive the packet.
- Candidate receivers evaluate their eligibility.
- Candidates independently calculate forwarding priority.
- Higher-priority candidates are scheduled to forward sooner.
- Lower-priority candidates suppress forwarding after detecting another successful transmission of the same packet, where reception is possible.
- Multiple hops are supported.
- Packet loops are prevented.
- Duplicate packets are detected.

The basic opportunistic protocol should use link quality and destination progress, but **must not use packet remaining lifetime in candidate selection**.

It may carry deadline metadata for fair accounting, but deadline information should not control forwarding in this baseline.

## 8.3 Protocol C: Deadline-Aware Opportunistic Routing

This is the proposed algorithm and the centerpiece of the project.

It must support every applicable capability of basic opportunistic routing, plus:

- Packet deadline tracking.
- Remaining-lifetime calculation.
- Deadline-aware eligibility decisions.
- Estimated downstream delivery delay.
- Queue-aware or processing-delay-aware decisions.
- Deadline-aware candidate priority.
- Packet expiration.
- Cancellation of expired scheduled transmissions.
- Per-class performance statistics.

It must make different forwarding decisions when remaining time changes.

The deadline-aware protocol must not be a cosmetic modification of the basic opportunistic protocol.

---

# 9. DESIGN THE DEADLINE-AWARE ALGORITHM

Implement a mathematically defensible and configurable candidate-selection algorithm.

The conceptual scoring formula in the abstract is:

```text
Score =
    Link Quality
  + Destination Progress
  + Remaining Lifetime
  - Expected Delay
```

However, this must be refined before implementation.

The quantities have different units, so directly adding them is incorrect.

Also, remaining lifetime can be identical for all candidates competing for the same packet, so merely adding it to every score does not meaningfully distinguish them.

Use normalized quantities and deadline feasibility constraints.

## 9.1 Time remaining

For each packet:

```text
remaining_time = expiry_time - current_simulation_time
```

Use `Simulator::Now()` for simulation time.

Do not use the host computer's wall clock.

If remaining time is zero or negative, the packet must not be newly forwarded.

## 9.2 Candidate eligibility

A node is a candidate only if:

- It is not the original sender receiving its own packet.
- It is not an invalid relay.
- It has not already forwarded the same packet.
- The packet hop limit has not been reached.
- The candidate makes appropriate progress or satisfies a documented loop-safe alternative.
- The packet remains valid.
- Its estimated future delivery time satisfies the selected deadline policy.

For the deadline-aware mode, require:

```text
estimated_remaining_delivery_delay
    + safety_margin
    <= remaining_packet_lifetime
```

The estimate must include relevant components such as:

```text
estimated_delivery_delay =
    candidate_processing_delay
  + estimated_queue_delay
  + anticipated_forwarding_wait
  + estimated_remaining_network_delay
```

Do not assume estimated delay is the same as the actual future delay.

It must be clearly identified as a prediction.

## 9.3 Destination progress

Using the node positions:

```text
progress =
    distance(previous_forwarder, destination)
  - distance(candidate, destination)
```

Define a normalized progress value.

Avoid choosing candidates that move a packet farther from the destination unless an explicitly implemented loop-safe recovery mechanism permits this.

If location knowledge is assumed, document it.

An acceptable design is to simulate GPS-like position announcements through neighbour-control packets.

Do not silently read every node's current global state to make perfect forwarding decisions.

Global topology knowledge may be used to construct the fixed baseline's initial route tables or to validate the simulation offline, but not as an invisible oracle for the proposed algorithm.

## 9.4 Link-quality estimation

Choose a feasible local measurement mechanism.

Examples:

- Periodic HELLO/beacon sequence numbers.
- Rolling beacon reception statistics.
- EWMA packet reception estimates.
- Observed transmission outcomes where acknowledgments exist.

Do not assign every node a perfect knowledge of future channel success.

If link reciprocity is assumed, state that assumption.

Explain what measurements are actually available to each node and how stale measurements are handled.

## 9.5 Downstream delay estimation

Use a defensible estimator based on some combination of:

- Estimated hop count.
- Current queue occupancy.
- Observed local transmission delays.
- Candidate distance to destination.
- Estimated per-hop forwarding delay.
- Relevant neighbor state.

Avoid using the packet's actual future delivery time.

The algorithm must make predictions using information available at decision time.

## 9.6 Normalized scoring

Implement a configurable score, for example:

```text
score =
    w1 * normalized_link_quality
  + w2 * normalized_progress
  + w3 * normalized_deadline_slack
  + w4 * normalized_queue_availability
```

The specific weights are illustrative.

Choose and document justified default weights.

All normalized components must have meaningful bounds.

Validate weights and reject invalid configurations.

For example:

```text
w1 + w2 + w3 + w4 = 1
```

or normalize valid positive weights internally.

For the basic opportunistic baseline, use a separate deadline-unaware score with comparable link-quality and progress inputs.

Perform a sensitivity analysis on algorithm weights if feasible.

## 9.7 Deadline feasibility and ranking

The proposed protocol should apply deadline feasibility before final ranking.

Calculate slack:

```text
slack =
    remaining_lifetime
  - estimated_remaining_delivery_delay
  - safety_margin
```

A non-positive slack makes the candidate deadline-infeasible under the estimator.

Rank feasible candidates using a documented score.

If no candidate is feasible, use a clearly documented policy, such as suppressing further forwarding of a packet that is predicted to miss its deadline.

Record the reason.

This behavior must be experimentally measurable.

## 9.8 Recheck before forwarding

An essential requirement:

A packet may be valid when its forwarding timer is scheduled but expired when the timer finishes.

Therefore:

**Check its deadline again immediately before transmission.**

A packet whose deadline has expired must not be forwarded simply because the timer was previously created.

---

# 10. FORWARDER COMPETITION AND COORDINATION

Implement a distributed forwarding coordination mechanism.

This must genuinely function in the simulation.

## 10.1 Priority-based timers

Map candidate priority onto a forwarding waiting interval.

For example:

```text
higher_score → shorter_wait
lower_score  → longer_wait
```

Use bounded, configurable timer ranges.

For instance:

```text
minimum_holdoff = 0.5 ms
maximum_holdoff = 5 ms
```

Treat these as tunable defaults, not fixed universal constants.

Use deterministic, bounded tie-breaking based on node ID, packet identity, and seed where practical.

The timer function must be monotonic with respect to priority.

## 10.2 Scheduling

Use actual NS-3 scheduling APIs.

Examples:

- `Simulator::Schedule()`.
- `Simulator::Cancel()`.
- `Simulator::Now()`.

Store the scheduled event identifier for each pending packet.

## 10.3 Duplicate suppression

Implement packet identity tracking.

Each node should distinguish states such as:

- Previously received.
- Pending forwarding.
- Already forwarded.
- Suppressed.
- Expired.

When a node overhears another forwarding transmission for the same packet, it should cancel its pending event according to the documented suppression rule.

Implement correct state transitions.

Do not merely drop duplicate packets at the destination while allowing unnecessary duplicate forwarding everywhere.

## 10.4 Hidden terminals and suppression failures

Do not assume that every candidate can overhear every other candidate.

Where nodes cannot hear one another, duplicates or collisions may occur.

Record these events.

Explain the limits of timer-based distributed coordination.

Do not suppress a packet using knowledge of another transmission that the node never actually received, unless a real control message communicates that information.

## 10.5 Duplicate-state cleanup

Packet-history structures must not grow without bound.

Implement expiration or bounded cleanup for old packet IDs.

Ensure cleanup does not accidentally permit looping within a still-active packet lifetime.

---

# 11. PACKET EXPIRATION AND QUEUE MANAGEMENT

Implement actual expiration handling.

Requirements:

1. Detect packets already expired upon reception.
2. Prevent expired packets from entering forwarding queues.
3. Remove or suppress expired pending forwarding events.
4. Recheck expiry before transmission.
5. Keep accurate drop-reason statistics.
6. Prevent deadline-aware packets from being forwarded indefinitely.
7. Limit maximum hop count.

Use correct absolute timestamps.

Track useful drop reasons, such as:

```text
EXPIRED_ON_RECEIVE
EXPIRED_BEFORE_FORWARD
DEADLINE_INFEASIBLE
HOP_LIMIT
DUPLICATE
NO_FORWARDING_CANDIDATE
QUEUE_OVERFLOW
INVALID_PACKET
```

Distinguish duplicate suppression, deadline expiration, and physical transmission loss.

Do not count them all as the same reason.

Implement realistic finite queue capacity and optional per-node processing delay.

Queue occupancy must affect the scheduling or processing behavior, not just appear in logging.

Do not use endless queues with zero processing time while claiming to evaluate congestion-aware forwarding.

---

# 12. IMPORTANT CORRECTNESS REQUIREMENTS

The following behaviors must be verified:

- A packet reaches the correct destination.
- A packet can travel over multiple hops.
- A packet can be received by multiple candidates.
- Candidate priorities can differ.
- A candidate can forward after a real simulation event.
- A lower-priority candidate can suppress a pending transmission by overhearing a forward.
- Duplicate delivery does not inflate unique delivery metrics.
- Packet deadlines are evaluated against the original creation time.
- Forwarding timers consume real simulation time.
- Expired packets cannot be newly forwarded by the proposed protocol.
- Queue delay is represented consistently.
- Deadline-aware forwarding can select a different relay from basic opportunistic forwarding in a controlled scenario.
- Changing mobility affects the underlying wireless network.
- Changing channel conditions affects reception statistics.
- Changing traffic load affects actual traffic generation.
- The three protocol identifiers execute different routing logic.

Implement assertions and tests wherever appropriate.

---

# 13. METRICS AND MEASUREMENTS

Develop a custom packet-level metrics collector.

NS-3 FlowMonitor may be used for suitable unicast diagnostic measurements, but it must not be the only metrics mechanism for this project because the proposed implementation involves broadcast forwarding.

All metrics must come from actual simulation events.

## 13.1 Packet Delivery Ratio

```text
PDR =
  unique_packets_delivered / packets_generated
```

Express as a percentage.

## 13.2 Deadline-Satisfied Delivery Ratio

This is the primary metric.

```text
DSDR =
  unique_packets_delivered_on_time / packets_generated
```

A packet delivered on time satisfies:

```text
arrival_time <= expiry_time
```

Use a consistent inclusive boundary.

## 13.3 End-to-End Delay

```text
end_to_end_delay =
    first_destination_arrival_time
  - original_creation_time
```

Calculate:

- Mean.
- Median.
- 95th percentile.

Clarify which packets are included.

By default, calculate these over uniquely delivered packets and expose an optional on-time-only view.

## 13.4 Expired Packets

Track:

- Unique packets dropped due to expiration.
- Expiration-related drop events.
- Packets whose deadlines are missed.
- Late deliveries.

These concepts are not interchangeable.

A deadline-missed packet can be lost, dropped, or delivered late.

Ensure the definitions are accurate.

## 13.5 Throughput

Calculate useful application-level throughput from unique delivered payload bytes over a documented measurement interval.

Report units such as kbps.

Do not count the same payload repeatedly because intermediate nodes forwarded it.

Optionally report raw channel traffic separately.

## 13.6 Forwarding Overhead

Track:

- Total forwarding transmissions.
- Forwarding attempts.
- Duplicate transmissions.
- Control-packet transmissions.
- Total transmitted bytes.

Use explicit definitions for overhead ratios.

## 13.7 Additional metrics

Where practical, include:

- Average hop count.
- Packet loss ratio.
- On-time deliveries per traffic class.
- Average forwarding wait.
- Duplicate-suppression count.
- Queue-drop count.
- Deadline-infeasible rejection count.
- Delivery ratio by node count.
- Delivery ratio by traffic load.
- Delivery ratio by deadline.

## 13.8 Conservation checks

Validate logical relationships.

For example:

```text
on_time_delivered <= unique_delivered
unique_delivered <= generated
late_delivered = unique_delivered - on_time_delivered
```

Some metrics count events while others count unique packets.

Never combine event counts and packet counts without explicitly defining the relationship.

Guard against division by zero, NaN, infinite results, and negative elapsed time.

---

# 14. LOGGING AND TRACE EXPORT

Implement structured trace logging.

Use CSV for broad compatibility and JSON for run metadata.

## 14.1 Packet event trace

Create a file such as:

```text
packet_events.csv
```

Possible columns:

```text
simulation_time_ms
event_type
packet_id
source_id
destination_id
current_node_id
previous_forwarder_id
traffic_class
creation_time_ms
expiry_time_ms
remaining_time_ms
hop_count
candidate_score
estimated_remaining_delay_ms
forwarding_wait_ms
queue_delay_ms
drop_reason
```

Use a consistent schema.

Record events such as:

```text
PACKET_CREATED
PACKET_TX
PACKET_RX
CANDIDATE_EVALUATED
FORWARD_SCHEDULED
FORWARD_EXECUTED
FORWARD_CANCELLED
DUPLICATE_SUPPRESSED
PACKET_EXPIRED
PACKET_DROPPED
DESTINATION_DELIVERED
```

Only emit event types that are backed by actual simulation behavior.

## 14.2 Packet summary

Export one logical record per generated packet:

```text
packet_summary.csv
```

Include:

- Packet identity.
- Source and destination.
- Traffic class.
- Creation time.
- Expiration time.
- Delivery status.
- First arrival time.
- On-time status.
- End-to-end delay.
- Hop count.
- Relevant terminal reason.

## 14.3 Node positions

Export positions at meaningful intervals:

```text
node_positions.csv
```

Include:

```text
simulation_time_ms
node_id
x
y
z
```

These must come from NS-3's actual MobilityModel.

## 14.4 Run metadata

Export:

```text
run_metadata.json
```

Include:

- NS-3 version.
- Git commit hash if available.
- Protocol.
- Topology.
- Node count.
- Simulation duration.
- Seed/run.
- Radio configuration.
- Mobility configuration.
- Traffic configuration.
- Deadline configuration.
- Algorithm parameters.
- Timestamp of execution.
- Relevant environment information.

## 14.5 Final metrics

Export:

```text
metrics.json
metrics.csv
```

Use a stable, documented schema.

---

# 15. CONFIGURATION AND COMMAND-LINE SUPPORT

Do not hardcode experimental values throughout the source files.

Create a single coherent configuration system.

Support values such as:

```text
protocol
topology
node_count
simulation_duration
seed
run_number
packet_size
packet_rate
traffic_model
mobility_model
mobility_speed
network_area
radio_range_or_propagation_parameters
deadline_emergency
deadline_video
deadline_normal
deadline_background
minimum_holdoff
maximum_holdoff
maximum_hops
queue_capacity
algorithm_weights
output_directory
```

Expose real command-line arguments in the NS-3 program.

Provide Python runner scripts that map validated YAML configurations to those command-line arguments.

Use actual supported argument names, confirmed by running the executable's help output.

Examples of desired user-facing commands:

```bash
python scripts/run_simulation.py \
  --protocol deadline_aware \
  --nodes 20 \
  --topology grid \
  --seed 42
```

```bash
python scripts/run_experiments.py \
  --config config/experiment-matrix.yaml
```

These are interface requirements; implement the commands rather than assuming the shown syntax already exists.

Validate user input.

Reject impossible node counts, invalid deadlines, unknown protocols, negative traffic rates, and invalid weights with helpful errors.

Generate unique output directories to avoid accidental result overwriting.

---

# 16. EXPERIMENT DESIGN

Run three forwarding protocols under comparable network scenarios.

The study must include varying:

1. Packet deadline.
2. Traffic load.
3. Node density.
4. Packet loss/channel quality.
5. Mobility.

## 16.1 Deadline experiment

Use several deadline settings across:

```text
50 ms
100 ms
200 ms
300 ms
500 ms
```

Also support the traffic-class default deadlines.

Use the same generated packet classes and deadline definitions across protocols.

Deadline-unaware baselines must still be evaluated against the packet deadlines.

## 16.2 Traffic load experiment

Use low, medium, and high traffic generation rates.

Choose values that produce measurably different offered loads under the configured radio setup.

Document the rates.

## 16.3 Node density experiment

Test:

```text
10 nodes
20 nodes
30 nodes
```

Add 50 nodes if performance and time permit.

Control whether network area is fixed or scaled.

Clearly identify how density changes.

## 16.4 Channel reliability experiment

Test favourable, moderate, and unfavourable channel conditions.

Vary actual model parameters.

Do not label a condition "high packet loss" unless the measured reception behavior supports it.

## 16.5 Mobility experiment

Compare static and mobile topologies.

Test meaningful mobility speeds.

## 16.6 Multiple seeds

For primary experiments, use at least five independent runs per protocol and scenario where feasible.

Prefer ten for stronger statistical estimates.

Use reproducible seed and run-number settings.

Try to keep exogenous scenario and traffic settings aligned across protocols.

Understand that protocol-dependent transmission behavior changes wireless contention, so individual radio outcomes will not always be identical.

Do not claim perfect paired channel realizations unless they are actually controlled.

## 16.7 Experiment matrix

Create a manageable baseline experiment matrix and an extended matrix.

A recommended initial matrix is:

- Three protocols.
- Three traffic loads.
- Three node densities.
- Five random seeds.

Then run deadline, mobility, and channel-loss sensitivity experiments separately.

Do not accidentally create an enormous Cartesian product that makes routine validation impractical.

## 16.8 Results integrity

Never fabricate experimental output.

Do not hardcode DSDR improvements.

Do not require the proposed method to win in every condition.

If the proposed method performs worse in a tested scenario, report the result and investigate why.

Possible legitimate causes include excessive holdoff, inaccurate delay estimates, missed forwarding opportunities, additional control overhead, or aggressive packet rejection.

---

# 17. AUTOMATED EXPERIMENT RUNNER

Implement a Python orchestration system.

Capabilities:

- Load experiment configuration.
- Validate the configuration.
- Build or locate the compiled NS-3 program.
- Run all selected combinations.
- Capture stdout and stderr.
- Record success or failure.
- Avoid overwriting previous results.
- Save run metadata.
- Continue appropriate independent experiments if one scenario fails.
- Aggregate completed results.
- Generate summary tables.
- Generate comparison figures.

Do not report failed runs as successful.

Support a `--dry-run` option that prints planned experiments without executing them.

Provide a clear progress display.

Experiment execution must use the real compiled simulator.

Do not silently substitute a random-number model if the simulator cannot start.

---

# 18. STATISTICAL ANALYSIS

Implement a defensible analysis pipeline.

Calculate:

- Mean metric values.
- Standard deviation.
- Confidence intervals where appropriate.
- Relative improvements.
- Per-scenario comparisons.

For example:

```text
DSDR improvement in percentage points =
    DSDR_proposed - DSDR_baseline
```

Clearly distinguish percentage-point changes from relative percentage changes.

For relative improvement:

```text
relative_improvement =
    (proposed - baseline) / baseline * 100
```

Handle zero baselines safely.

When using confidence intervals, document the method and sample size.

Avoid presenting statistical significance from a single simulation seed.

Include interpretation of meaningful tradeoffs.

Examples:

- More on-time packets but higher overhead.
- Lower delay but fewer total deliveries.
- Stronger performance under congestion.
- No improvement in low-loss networks.
- Sensitivity to estimated delay accuracy.

---

# 19. GENERATE PROFESSIONAL GRAPHS

The project must automatically generate publication-quality figures from actual experiment results.

Minimum plots:

1. Packet Delivery Ratio versus routing protocol.
2. Deadline-Satisfied Delivery Ratio versus routing protocol.
3. Average end-to-end delay versus routing protocol.
4. Deadline satisfaction versus packet deadline.
5. DSDR versus traffic load.
6. DSDR versus number of nodes.
7. DSDR versus channel quality.
8. Expired packet count comparison.
9. Forwarding overhead comparison.
10. Duplicate transmission comparison.
11. Throughput comparison.
12. Delay distribution comparison.

Use consistent protocol names and distinguishable colors.

All charts must include:

- Descriptive titles.
- Clearly labeled axes.
- Units.
- Legends where applicable.
- Appropriate scales.
- Data-source identification in generated reports.

Use confidence intervals for aggregated experiments where available.

Export PNG and SVG where practical.

Optionally generate a combined PDF of all result figures.

No example values should be included in final research figures as if they were genuine results.

---

# 20. CREATE AN INTERACTIVE DASHBOARD

This is important for the project demonstration.

Build a polished, usable dashboard using Streamlit and Plotly.

Give it the title:

**Deadline-Aware Opportunistic Routing Lab**

The interface should feel like an engineering research tool rather than an ordinary form displaying a few numbers.

Use a clean professional visual design.

Suggested visual identity:

- Dark navy or charcoal background option.
- Blue for conventional routing.
- Amber for basic opportunistic routing.
- Green or teal for deadline-aware routing.
- Clear cards, spacing, and typography.
- Responsive layout where supported.

Do not compromise scientific correctness for visual effects.

## 20.1 Dashboard overview

Display:

- Selected routing protocol.
- Node count.
- Packets generated.
- Packets delivered.
- On-time deliveries.
- PDR.
- DSDR.
- Average delay.
- Expired packets.
- Forwarding overhead.

All displayed statistics must be computed from selected real result files.

## 20.2 Simulation controls

Provide interactive settings for:

- Protocol.
- Node count.
- Topology.
- Traffic rate.
- Deadlines.
- Mobility.
- Seed.
- Available channel configurations.

When an NS-3 runtime is available, allow the user to launch a new simulation.

Validate inputs before invoking the simulator.

Use safe subprocess APIs with argument arrays rather than shell interpolation.

Show actual execution status and error messages.

If the runtime is unavailable, allow existing results to be explored and explain that new simulations require NS-3.

## 20.3 Network topology view

Display nodes with their actual positions.

Distinguish:

- Source.
- Destination.
- Other nodes.

Show packet forwarding events between transmitting and receiving nodes based on actual recorded events.

Do not draw a successful packet transmission to a node unless the event data supports it.

## 20.4 Packet animation

Provide a timeline-based playback interface.

Features:

- Play/pause.
- Timeline slider.
- Step through events.
- Packet ID selection.
- Playback-speed selection.
- Protocol selection.

Animate events such as:

```text
Packet created
Packet transmitted
Packet received
Candidate evaluated
Forward scheduled
Forward suppressed
Packet forwarded
Packet expired
Packet delivered
```

Use actual timestamps and exported node positions.

If visual interpolation is applied between recorded states, identify it as an animation aid, not an additional physical simulation.

## 20.5 Candidate-decision explorer

This page should demonstrate the main research contribution.

For a selected real packet and forwarding event, show:

- Which node received it.
- Remaining deadline.
- Estimated downstream delay.
- Link-quality estimate.
- Destination progress.
- Queue information.
- Candidate score.
- Eligibility decision.
- Chosen forwarding timer.
- Final forwarding result.

Allow the user to understand why one candidate forwarded and another did not.

When comparing protocols, only place decisions side by side when the runs are meaningfully comparable.

Do not imply that packets from different stochastic executions followed the same physical trajectory.

## 20.6 Algorithm comparison

Allow comparison of the three protocols.

Display:

- DSDR.
- PDR.
- Delay.
- Throughput.
- Forwarding overhead.
- Duplicate transmissions.
- Expiration metrics.

Support filtering by:

- Scenario.
- Node count.
- Traffic class.
- Deadline.
- Seed.
- Traffic load.

## 20.7 Experiment explorer

Allow selection of previously executed experiments.

Display graphs and aggregate statistics from stored data.

Provide CSV downloads and report exports.

## 20.8 Methodology page

Include a short explanation of:

- What NS-3 simulates.
- How each routing mode works.
- How forwarding competition works.
- How deadlines are evaluated.
- Which metrics are collected.
- The main modeling assumptions.

Make the dashboard understandable to a college project evaluator.

## 20.9 Dashboard reliability

The dashboard must:

- Handle missing results.
- Handle empty result files.
- Handle malformed CSV data.
- Avoid crashing when a metric is unavailable.
- Explain when no experimental runs exist.
- Never display fake research results as actual results.

Use schema validation where appropriate.

---

# 21. SPECIAL DEMONSTRATION SCENARIOS

Create deterministic or tightly controlled experiments specifically for classroom demonstrations.

These must still execute through the NS-3 simulator.

## Demo 1: Basic wireless packet delivery

A sends a packet that a nearby node receives.

Show the packet's actual send and receive timestamps.

## Demo 2: Multiple wireless receivers

A broadcasts packet 101.

Both B and C receive the packet.

Log both receptions.

Demonstrate that receiving the same broadcast does not mean both nodes must forward.

## Demo 3: Duplicate suppression

Both B and C initially become eligible forwarding candidates.

C receives the higher priority.

C forwards first.

B detects C's transmission and cancels its own scheduled forwarding event.

Construct the topology so B can actually overhear C.

Show the event sequence in the trace.

## Demo 4: Deadline-aware decision

Construct a topology and processing/queue conditions where:

- B has a better estimated link.
- C has a shorter estimated remaining delivery time.
- A packet has a tight deadline.

Verify that the deadline-aware algorithm selects the feasible faster candidate under the configured decision model.

Compare this with the basic opportunistic candidate ranking.

The differences must arise from the implemented scoring and scheduling logic.

## Demo 5: Packet expiration

Generate a packet with a very short deadline.

Ensure it expires before the next scheduled forwarding event.

Verify:

- The expiration is logged.
- The forwarding timer does not transmit it.
- The appropriate drop counter is incremented.

## Demo 6: Multi-hop delivery

Show a packet moving through several intermediate nodes before reaching the destination.

## Demo 7: Congestion

Increase traffic so queues and contention become meaningful.

Compare the algorithms under this increased load.

## Demo 8: Mobility

Move nodes during the simulation.

Show that wireless reception and available forwarding opportunities change.

Create a single command or simple dashboard selector to execute these demonstration scenarios.

---

# 22. AUTOMATED TESTS

A complete implementation requires real tests.

## 22.1 Packet tests

Verify:

- Serialization.
- Deserialization.
- Timestamp preservation.
- Packet ID preservation.
- Hop count.
- Invalid header handling.

## 22.2 Deadline tests

Test:

- Positive remaining time.
- Zero remaining time.
- Negative remaining time.
- Boundary arrival exactly at the deadline.
- Expiration while queued.
- Expiration while awaiting forwarding.

## 22.3 Scoring tests

Verify:

- Normalized scores are bounded.
- Weights are validated.
- Increasing expected delay reduces the appropriate deadline-aware preference.
- Better deadline feasibility changes priority under controlled conditions.
- Deadline-unaware scoring does not use deadline values.
- Ties are handled reproducibly.

## 22.4 Forwarding tests

Verify:

- Fixed next-hop forwarding.
- Basic opportunistic forwarding.
- Deadline-aware forwarding.
- No invalid self-forwarding.
- Hop limits.
- Multi-hop delivery.
- Forwarder-timer ordering.
- Duplicate cancellation.
- Hidden-node cases where suppression may fail.

## 22.5 Metrics tests

Verify metric calculations using small known input datasets.

For example:

```text
Generated = 100
Unique delivered = 75
On-time delivered = 60
Late delivered = 15
```

Expected:

```text
PDR = 75%
DSDR = 60%
```

These values are for unit testing only, not final project research results.

## 22.6 Configuration tests

Validate all important command-line and configuration inputs.

## 22.7 Integration tests

Run actual NS-3 simulation tests.

At minimum:

- Four-node smoke run.
- Static multi-hop run.
- Opportunistic candidate run.
- Deadline-aware run.
- Mobility run.
- Congestion run.

## 22.8 Reproducibility tests

Execute the same deterministic configuration twice with the same seed, run number, and code version.

Verify expected reproducibility of generated packet and event statistics.

Do not compare wall-clock execution timestamps or output-directory names.

## 22.9 Dashboard tests

Test result loading, metrics display logic, data filters, and handling of missing files.

Use a Streamlit-compatible testing approach where practical.

---

# 23. INSTALLATION AND REPRODUCIBILITY

Provide a reliable setup workflow.

## 23.1 Environment detection

Before installation, inspect:

- Operating system.
- C++ compiler.
- CMake.
- Python version.
- Available NS-3 installation.
- Git.
- Required libraries.

Report missing dependencies.

## 23.2 NS-3 integration

Support a configurable `NS3_DIR` path.

For example:

```bash
export NS3_DIR=/path/to/ns-3.45
```

The project must work with the documented NS-3 version.

Do not hardcode the developer's personal home directory.

Use a safe build integration that does not overwrite arbitrary existing NS-3 source files.

## 23.3 Setup script

Create:

```bash
bash scripts/setup.sh
```

The setup should:

- Verify dependencies.
- Create the Python environment as appropriate.
- Install Python requirements.
- Detect or guide installation of NS-3.
- Integrate project source files safely.
- Configure the build.
- Report success or actionable errors.

Do not issue privileged system modifications without permission.

If network access or privilege escalation is unavailable, document what is blocked and continue implementing everything that can be completed locally.

## 23.4 Build script

Create:

```bash
bash scripts/build.sh
```

The build script should:

- Find NS-3.
- Configure the required target.
- Compile the project.
- Detect compiler errors.
- Return the correct exit status.

## 23.5 Easy commands

Create convenient targets such as:

```bash
make setup
make build
make smoke
make test
make demo
make experiment
make analyze
make dashboard
```

Implement only real targets and document their behavior.

Avoid commands that silently run unrelated or destructive operations.

## 23.6 Clean repository

Add a correct `.gitignore` for:

- NS-3 build files.
- Python virtual environments.
- Caches.
- Temporary outputs.
- Logs.
- Large generated datasets.

Keep required source code, configuration, small verified test fixtures, and documentation in version control.

---

# 24. DOCUMENTATION

Provide a professional README.

It should explain:

1. Project title and objective.
2. Research problem.
3. Why deadline-aware forwarding matters.
4. The three routing approaches.
5. Technologies used.
6. Installation.
7. Building.
8. Running a basic simulation.
9. Running experiment batches.
10. Opening the dashboard.
11. Reading the results.
12. Project structure.
13. Testing commands.
14. Limitations.
15. Reproducibility.

A new developer should be able to follow the README without knowing the internal implementation.

## 24.1 Architecture document

Include diagrams for:

- NS-3 network architecture.
- Packet life cycle.
- Forwarding decision logic.
- Candidate coordination.
- Metrics pipeline.
- Dashboard data flow.

Mermaid diagrams inside Markdown are acceptable.

## 24.2 Algorithm document

Explain:

- Input parameters.
- Mathematical formulas.
- Normalization.
- Deadline feasibility.
- Link-quality estimation.
- Delay estimation.
- Priority calculation.
- Timer scheduling.
- Duplicate suppression.
- Packet expiration.
- Algorithmic limitations.

Include readable pseudocode consistent with the actual implementation.

## 24.3 Experiment methodology

Explain:

- Network topologies.
- Radio settings.
- Propagation models.
- Mobility models.
- Traffic models.
- Random seeds.
- Parameter settings.
- Baseline fairness.
- Data collection.
- Statistical analysis.

## 24.4 Final academic report

Prepare a formal project report with:

- Title.
- Abstract.
- Introduction.
- Problem statement.
- Motivation.
- Objectives.
- Related work.
- System architecture.
- Proposed methodology.
- Algorithm.
- Implementation details.
- Experimental setup.
- Performance metrics.
- Results and analysis.
- Discussion.
- Limitations.
- Future work.
- Conclusion.
- References.

Use actual results once produced.

Use verifiable references for related work.

Do not fabricate papers, authors, DOI identifiers, or research claims.

Do not present expected outcomes as experimentally demonstrated findings.

## 24.5 Presentation guide

Write a faculty-presentation guide explaining:

- What problem is being solved.
- Why deadlines matter.
- Why traditional forwarding may fail.
- What opportunistic routing changes.
- What the proposed algorithm adds.
- How NS-3 simulates the network.
- How forwarding candidates compete.
- How duplicate suppression works.
- How performance is evaluated.
- What the results mean.

Include a demonstration sequence suitable for a presentation.

## 24.6 Viva preparation

Create at least 20 technically accurate viva questions with concise answers.

Cover:

- NS-3.
- Network simulator versus real network.
- Wi-Fi broadcasting.
- Routing.
- Opportunistic forwarding.
- Deadlines.
- Packet loss.
- Propagation.
- Queueing.
- End-to-end delay.
- Packet delivery ratio.
- Deadline-satisfied delivery ratio.
- Duplicate suppression.
- Event scheduling.
- Algorithm selection.
- Simulation assumptions.
- Interpretation of results.

---

# 25. SCIENTIFIC AND TECHNICAL HONESTY

Maintain a clear distinction between:

1. A simulation.
2. A real deployment.
3. An estimated quantity.
4. An observed quantity.
5. A predicted result.
6. An experimentally measured result.

Do not claim the simulation guarantees real-world emergency delivery performance.

Do not claim that the proposed algorithm always improves DSDR.

Do not claim to have implemented IP-layer routing if the actual logic is at the application layer over UDP.

Do not use simulator-global knowledge to give the algorithm unrealistic information.

Do not claim an actual packet transmission happened when the simulator merely scheduled a timer.

Do not hide duplicate packets from statistics.

Do not claim a unit test proves the full wireless network works.

Do not silently ignore failed experiments.

Prefer an honestly validated implementation over impressive-looking but unverifiable features.

---

# 26. PERFORMANCE AND SOFTWARE QUALITY

Use:

- Clear class responsibilities.
- Modern C++ idioms supported by NS-3.
- RAII where appropriate.
- Explicit configuration.
- Meaningful names.
- Reasonable error handling.
- Minimal global mutable state.
- Reusable scoring functions.
- Deterministic testing.
- Clean data schemas.
- Efficient event logging.

Avoid:

- Monolithic functions where modular design is practical.
- Silent exception suppression.
- Magic numbers scattered throughout the code.
- Copy-paste implementations of almost identical logic.
- Endless packet-state storage.
- Hardcoded result values.
- Unsafe system commands.
- Pseudocode masquerading as an implementation.
- GUI features disconnected from the simulator.

Include comments explaining networking decisions and non-obvious algorithm logic.

Comments should explain why something is done, not merely repeat the code.

---

# 27. REQUIRED VALIDATION EVIDENCE

Create:

```text
evidence/validation.md
```

This file must record genuine verification performed in the execution environment.

Include:

- Operating system.
- Compiler version.
- Python version.
- NS-3 version.
- Exact build command.
- Build outcome.
- Smoke-test commands.
- Test results.
- Successful simulation commands.
- Experiment commands actually executed.
- Output files actually generated.
- Known issues.
- Remaining limitations.

Do not invent validation evidence.

If NS-3 cannot be installed or executed because of the environment, record the limitation.

Still implement and test all available components, but do not falsely describe the entire project as runtime-verified.

---

# 28. DEFINITION OF DONE

Do not mark the project complete unless the following checks pass, or explicitly identify why a check is blocked.

## Core implementation

- [ ] NS-3 simulator builds.
- [ ] A real Wi-Fi network is instantiated.
- [ ] Nodes have actual wireless interfaces.
- [ ] Packets are transmitted over NS-3 networking models.
- [ ] Multiple receivers can receive a broadcast.
- [ ] Packets can reach destinations over multiple hops.
- [ ] Fixed-next-hop forwarding works.
- [ ] Basic opportunistic forwarding works.
- [ ] Deadline-aware forwarding works.
- [ ] All three modes use distinct verified logic.
- [ ] Candidate scoring works.
- [ ] Deadline feasibility works.
- [ ] Forwarder timers work.
- [ ] Duplicate suppression works.
- [ ] Packet expiration works.
- [ ] Queue behavior is represented.
- [ ] Mobility affects network conditions.
- [ ] Channel conditions affect reception.

## Measurement and experiments

- [ ] Generated packets are counted correctly.
- [ ] Unique delivered packets are counted correctly.
- [ ] On-time deliveries are counted correctly.
- [ ] Late deliveries are counted correctly.
- [ ] End-to-end delay is calculated correctly.
- [ ] Duplicate transmissions are tracked.
- [ ] Expiration events are tracked.
- [ ] Structured traces are exported.
- [ ] Multiple seeds can be executed.
- [ ] Experiment batches can be run.
- [ ] Statistical aggregation works.
- [ ] Real graphs can be generated.

## User-facing features

- [ ] Dashboard launches.
- [ ] Dashboard loads real result files.
- [ ] Network topology appears correctly.
- [ ] Packet-event visualization works.
- [ ] Candidate-decision explorer works.
- [ ] Protocol comparison works.
- [ ] Experiment selection works.
- [ ] Invalid input is handled correctly.

## Delivery

- [ ] Setup instructions are complete.
- [ ] Tests are included.
- [ ] Tests have been run where possible.
- [ ] README is accurate.
- [ ] Architecture is documented.
- [ ] Algorithm is documented.
- [ ] Experiment design is documented.
- [ ] Final report exists.
- [ ] Presentation guide exists.
- [ ] Reproducibility instructions exist.
- [ ] Remaining limitations are documented.

---

# 29. IMPLEMENTATION STRATEGY

Implement the project in the following order.

This is an internal execution order, not a request to stop after each stage.

## Stage 1: Repository and environment

Inspect the current directory.

Identify any existing project files.

Determine OS, compiler, Python, and NS-3 availability.

Select a compatible NS-3 version.

Create the appropriate project structure and build integration.

## Stage 2: Working wireless communication

Implement a minimal, functioning NS-3 wireless network.

Verify a real packet is sent and received through the Wi-Fi stack.

Preserve this as an automated regression test.

## Stage 3: Multi-hop packet handling

Implement packet serialization, reception callbacks, and forwarding.

Verify multi-hop delivery and packet identity tracking.

## Stage 4: Fixed-next-hop baseline

Implement the first fully functioning protocol.

Measure packet delivery and end-to-end delay.

## Stage 5: Opportunistic forwarding

Implement multiple forwarding candidates, scoring, timers, and duplicate suppression.

Verify the diamond topology.

## Stage 6: Deadline-aware forwarding

Implement deadline metadata, expiry checks, delay prediction, feasibility, scoring, and timer cancellation.

Verify that deadlines influence candidate selection.

## Stage 7: Realistic network conditions

Integrate radio configuration, queueing, loss, and mobility.

Ensure these systems actually affect routing outcomes.

## Stage 8: Metrics

Implement reliable packet tracking, counters, and trace exports.

Add validation checks.

## Stage 9: Experiments

Implement scenario configurations, automated batch execution, and repeated seeds.

Run smoke and representative experiments.

## Stage 10: Analysis

Implement aggregation, confidence intervals, comparison charts, and reporting.

## Stage 11: Interactive dashboard

Implement the polished dashboard using real traces and metrics.

## Stage 12: Testing and documentation

Run all available tests.

Fix defects.

Generate real validation evidence.

Complete README, project report, diagrams, and presentation documentation.

## Stage 13: Final verification

Perform a full end-to-end test:

```text
Environment setup
       ↓
Project build
       ↓
NS-3 simulation
       ↓
Packet-level trace export
       ↓
Metrics computation
       ↓
Experiment comparison
       ↓
Graph generation
       ↓
Interactive visualization
       ↓
Academic report
```

Every arrow must correspond to a functioning integration.

---

# 30. INSTRUCTIONS FOR HOW YOU MUST WORK

This section is extremely important.

You are an autonomous coding agent tasked with implementing the project.

Follow these principles.

### A. Execute instead of only describing

Do not respond with a lengthy development plan and stop.

Inspect the repository and start creating source files.

### B. Verify each stage

After implementing a major subsystem:

- Build it.
- Run relevant tests.
- Inspect failures.
- Correct errors.
- Continue.

### C. Do not leave hidden placeholders

Do not write:

```cpp
// TODO: implement routing
```

and then claim routing is complete.

A known unfinished feature must be reported explicitly.

### D. Do not fake results

If simulation data has not been generated, say so.

Use genuine run outputs for demonstration figures.

### E. Prioritize actual networking correctness

A functional NS-3 routing core is more important than a beautiful dashboard with no real simulation.

Build the core before investing heavily in the UI.

### F. Preserve reproducibility

Use documented configurations, seeds, build steps, and output schemas.

### G. Handle compatibility properly

Inspect the actual NS-3 source/API before implementing unsupported functions.

Compile against the target version.

Avoid speculative fixes and outdated syntax.

### H. Maintain implementation notes

Keep a short implementation checklist or progress document updated as work proceeds.

Record completed components and verified commands.

### I. Continue through problems

If the build fails, diagnose and fix it.

If tests fail, correct the implementation and rerun them.

If a dependency is missing, use an appropriate safe installation or document the genuine external blocker.

Do not give up after the first failure.

### J. Do not perform unauthorized external actions

You may modify project files in the authorized workspace and execute appropriate local build/test commands.

Do not delete unrelated files, push to remote repositories, create public releases, or change account settings without authorization.

### K. Keep the implementation honest

If a requirement is infeasible within the available environment, explain the reason, implement the best correct alternative, and identify the difference.

Do not reduce the project to a toy simulator while continuing to claim full compliance.

### L. Use the available reasoning and execution context

Since this is a complex engineering task, maintain a coherent architecture and continue the implementation rather than repeatedly redesigning the project.

When context or execution limits interrupt work, save concrete progress in repository documentation so that work can resume without losing the design.

---

# 31. EXPECTED FINAL PROJECT DEMONSTRATION

A successful demonstration should look approximately like this:

**Step 1:** Launch the dashboard or command-line experiment selector.

**Step 2:** Select a 10-node wireless network.

**Step 3:** Select conventional fixed-next-hop forwarding.

**Step 4:** Run the actual NS-3 simulation.

**Step 5:** Display packet transmission events, delivery statistics, and missed deadlines.

**Step 6:** Select basic opportunistic forwarding.

**Step 7:** Run a comparable simulation and visualize multiple receiving candidates.

**Step 8:** Select deadline-aware opportunistic forwarding.

**Step 9:** Run a comparable simulation and inspect candidate feasibility, scoring, and timer decisions.

**Step 10:** Compare measured on-time delivery, delay, losses, and overhead for all three approaches.

**Step 11:** Run a controlled diamond-topology demonstration and show why the deadline-aware algorithm can choose a different forwarding candidate.

**Step 12:** Open experiment graphs and explain the results.

**Step 13:** Export the real experimental results and an academic report.

The project should demonstrate the network behavior clearly enough that a faculty evaluator can understand both the Computer Networks concepts and the proposed algorithm.

---

# 32. FINAL DELIVERABLES

At the conclusion, the workspace should contain:

1. Functional NS-3 C++ source code.
2. Three working forwarding protocols.
3. Working packet-deadline and coordination logic.
4. Configurable wireless simulation scenarios.
5. Simulation launch scripts.
6. Automated experiment runner.
7. Packet-level traces and metrics collector.
8. Python analysis pipeline.
9. Interactive dashboard.
10. Real result visualizations.
11. Automated tests.
12. Installation and build instructions.
13. Technical and academic documentation.
14. Formal report.
15. Presentation and viva preparation material.
16. Validation evidence with genuine test results.

Provide a concise final engineering report covering:

- What was implemented.
- Which tests passed.
- Which demonstrations ran successfully.
- How to launch the full application.
- Where experiment results are stored.
- Which assumptions were made.
- Which limitations remain.

Do not describe untested features as verified.

---

# 33. FINAL QUALITY EXPECTATION

This project must combine four qualities:

**Computer Networks correctness:** actual NS-3 wireless transmission, routing decisions, packet forwarding, and measurable network behavior.

**Algorithmic substance:** a genuine deadline-aware candidate-selection algorithm with time feasibility, delay estimation, and forwarding coordination.

**Research quality:** fair comparisons, reproducible experiments, appropriate metrics, and honest interpretation.

**Presentation quality:** an understandable dashboard, clear network animations, professional graphs, organized documentation, and a strong demonstration narrative.

The final result should be suitable for:

- A Computer Networks semester project.
- A complete technical demonstration.
- Faculty review and viva.
- A professional GitHub portfolio.
- Further research and experimentation.

**The objective is a robust, functioning engineering project—not simply a large quantity of generated code.**

---

# 34. START IMPLEMENTATION NOW

Begin by inspecting the current workspace and environment.

Then:

1. Identify the correct NS-3 build and integration approach.
2. Create the project architecture.
3. Implement the core wireless simulation.
4. Build and execute it.
5. Implement the three forwarding protocols.
6. Validate the deadline-aware algorithm.
7. Complete the experiment and visualization pipeline.
8. Run tests and real experiments.
9. Generate genuine outputs and documentation.
10. Verify the end-to-end workflow.

Do not finish after generating a project plan.

Do not declare the project complete based only on source-file creation.

**Start coding now and continue working toward the complete verified implementation.**