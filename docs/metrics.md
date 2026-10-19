# Trace and metric definitions

Times in CSV are milliseconds; transmitted times are integer nanoseconds. Packet IDs
are exact unsigned 64-bit integers derived from source/sequence. One summary record
exists for each PACKET_CREATED event. First correct-destination delivery determines
arrival, delay, hop count and inclusive on-time status. Duplicate copies never inflate PDR.

| Metric | Definition |
|---|---|
| PDR (%) | 100 × unique delivered / generated |
| DSDR (%) | 100 × unique delivered by expiry / generated |
| Late delivered | unique delivered minus on-time |
| Deadline missed | not on-time, with expiry at or before simulation stop |
| Undelivered | generated without observed destination delivery at stop |
| Delay | first arrival minus creation, delivered packets only |
| Throughput (kbps) | unique delivered payload bytes × 8 / full duration / 1000 |
| Forwarding transmissions | successful UDP submissions by non-source relays |
| Forwarding attempts | executed forwarding timers, including no-route outcomes |
| Duplicate transmissions | extra data UDP submissions at the same packet/hop depth |
| Control transmissions | successful HELLO UDP submissions |
| UDP protocol bytes | payload plus 76-byte header for data, 76 bytes per HELLO |
| PHY transmissions | actual Wi-Fi PHY transmission-start callbacks, all frame kinds |
| PHY receive drops | real PHY drop callback events, not unique end-to-end losses |
| Unique expired | identities with at least one local expiration event |
| Expiration events | all local PACKET_EXPIRED events |
| Queue drops | finite application queue rejection events |
| Infeasible events | candidate decisions rejected by deadline feasibility |

`PACKET_TX` denotes a socket-accepted UDP submission, not a guarantee of PHY airtime.
Use `radio_events.csv` for actual airtime events; that trace includes non-data frames
and does not claim a reliable mapping from every radio failure to an end-to-end packet.
The redundancy metric counts extra branches at the same depth; it is not all causally
unnecessary transmissions or an omniscient optimal-route comparison.

`observed_drop_reasons` summarizes branch-local evidence. `terminal_status` is delivered
on time, delivered late, or undelivered at simulation stop. Do not relabel all undelivered
packets as physical losses. Queue drops, no-progress and late traffic can all contribute.
If stop precedes an undelivered packet's deadline, it is counted separately as
`deadline_pending_at_stop`, not as a confirmed miss. The primary matrix drains through
all configured deadlines. DSDR is the fraction observed on time by stop.

Conservation checks require on-time ≤ delivered ≤ generated and nonnegative delay.
A packet can be expired on one branch and delivered on another, so unique-expired is
not additive with delivered. Empty denominators produce zero PDR/DSDR; undefined delay
and overhead per delivery are JSON null, not fabricated zero values.
