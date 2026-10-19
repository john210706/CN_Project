# Algorithm and wire format

The protocol is an Application on each NS-3 node using UDP port 9000. Every hop
broadcasts an actual Wi-Fi packet. A 76-byte, network-order header carries version,
kind (DATA/HELLO), class, source, destination, sequence, last forwarder, designated
next hop, creation/expiry in integer ns, hop count/limit, sender and target coordinates
in signed mm, queue occupancy, processing time in μs, HELLO sequence and payload size.
Identity is `(source << 32) | sequence`. Packet size excludes the 76-byte protocol
header in user settings. Header size/version/node references/payload length are checked.

## Knowledge and estimators

Each receiver knows its own MobilityModel position. Sender coordinates are serialized
at transmission. Destination coordinates come from the source's **initial configured
mission location**, not from a simulator-global runtime lookup. This assumes prior
location provisioning; a mobile destination can outrun its advertised target.

Every node broadcasts HELLOs at the configured interval, staggered initially by node ID.
Receiver-local link quality `q` is the count of received beacons in the last ten beacon
intervals divided by the observed sequence span plus estimated missing tail beacons.
Neighbors expire after five intervals without updates; unseen neighbors have q=0.
No outgoing ACK or future reception information is available. Using incoming reception
as a preference is a heuristic, not a measured downstream success probability.

Let R be expiry minus current simulation time, d the candidate-to-target distance,
p the reduction in distance from sender to candidate, r the configured hop scale,
P the node's processing time, Q the already reserved processing workload, and H the
configured predicted downstream time per hop. Units below are milliseconds.

```
g = clamp(p / r, 0, 1)
D0 = P + Q + ceil(d / r) * H
s0 = clamp((R - D0 - safety) / max(R, epsilon), 0, 1)
a = 1 / (1 + Q / max(P, 0.1))
score_basic = 0.5*q + 0.5*g
score_deadline = w_link*q + w_progress*g + w_slack*s0 + w_queue*a
wait = min_holdoff + (1-score)*(max_holdoff-min_holdoff)
estimated_delay = D0 + wait
slack = R - estimated_delay - safety
```

Defaults are weights 0.3/0.3/0.3/0.1, processing 1 ms, holdoff 0.5–5 ms,
safety 0.5 ms and predicted downstream 3 ms/hop. Weights are finite, nonnegative,
and sum to one. These are interpretable starting parameters, not empirically optimal
values. The extended experiment matrix changes weights for sensitivity analysis.

Positive progress is required. Deadline-aware candidates additionally require positive
slack, so equality is rejected conservatively. Delivery accounting is separately inclusive:
arrival exactly at expiry is on time. Basic opportunistic scoring and eligibility ignore R.

Ranking slack excludes holdoff to avoid circularity; feasibility then includes the chosen
holdoff. A deterministic <1 μs node/packet/seed tie-break is added. It is much smaller
than the default safety margin. It perturbs strict timer ordering only for effectively
equal scores. Queue processing and radio contention can change the observed transmit order.

## Processing and coordination

```
on first eligible reception:
    if hop limit reached: record HOP_LIMIT
    if pending capacity full: record QUEUE_OVERFLOW
    reserve a serial processing slot after existing reserved work
    schedule forwarding at slot finish + holdoff
    in deadline-aware mode: also schedule cancellation at absolute expiry
on an actually received downstream copy while pending:
    cancel forwarding and expiry events; record suppression
on forwarding event:
    recheck deadline; expired packets never enter a new UDP send
    increment hop count, serialize current position, send broadcast
on first reception at destination:
    record delivery, including late delivery; retain identity
```

A receiver cancels only if the overheard copy's hop count exceeds the stored copy's
hop count. Same-depth competing receptions do not automatically cancel one another.
There is no out-of-band winner notification. Hidden candidates can transmit duplicates.
Each node forwards a given identity at most once within the history horizon. Strict
geographic progress for the transmitted target and hop limits provide further protection.

History retention ends at expiry plus a conservative finite forwarding-work horizon:
`maxHops*(queueCapacity*max_processing + max_holdoff) + 1000 ms`. Later copies are
rejected as HISTORY_HORIZON; cleanup runs every second. Memory scales with arrivals
inside this horizon, not with an unlimited simulation duration. This is a memory bound,
not a claim about worst-case Wi-Fi latency. Baselines remain deadline-unaware within
the horizon and can produce late deliveries.

Cancellation releases pending capacity but does not reclaim the serial processing
reservation. This models committed work; it can overestimate subsequent queue delay.
The application queue is distinct from the real Wi-Fi MAC queue. Once UDP accepts a
packet, the application's expiry event cannot retract that packet from the MAC.
