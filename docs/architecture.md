# Architecture

```mermaid
flowchart LR
  YAML[Validated YAML] --> Runner[Python launcher]
  Runner --> Sim[NS-3 C++ program]
  Sim --> Mobility[MobilityModel]
  Sim --> App[Per-node forwarding application]
  App --> UDP[UDP / IPv4]
  UDP --> MAC[Ad-hoc Wi-Fi MAC]
  MAC --> PHY[Yans PHY and propagation]
  PHY --> RX[Other nodes' real receive stacks]
  RX --> App
  Sim --> Trace[CSV traces and metadata]
  Trace --> Metrics[Unique packet accounting]
  Metrics --> Stats[Independent-seed statistics]
  Stats --> Figures[PNG / SVG / report]
  Trace --> Dashboard[Streamlit event playback]
```

```mermaid
stateDiagram-v2
  [*] --> Created
  Created --> Pending: finite queue admits
  Created --> Dropped: overflow
  Pending --> Expired: deadline event
  Pending --> Suppressed: received downstream forward
  Pending --> Transmitted: processing and timer finish
  Transmitted --> Received: successful radio reception
  Received --> Delivered: correct destination
  Received --> Pending: eligible first copy
  Received --> Dropped: infeasible / duplicate / hop limit
```

```mermaid
sequenceDiagram
  participant A as Sender A
  participant B as Candidate B
  participant C as Candidate C
  participant Z as Destination Z
  A->>B: Real Wi-Fi reception
  A->>C: Real Wi-Fi reception
  B->>B: Score and schedule
  C->>C: Score and schedule
  C->>Z: Forward after timer
  C->>B: Overheard downstream packet
  B->>B: Cancel pending event
```

Reception arrows describe possible recorded events, not guaranteed channel delivery.
Trace collection is global only for offline measurement; the forwarding app never reads
another app's state or a future trace. The fixed baseline alone receives initial BFS tables.
