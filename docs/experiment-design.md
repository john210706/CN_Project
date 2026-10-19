# Experiment design

`config/experiment-matrix.yaml` is the executable primary design. Each named scenario
runs fixed, opportunistic and deadline-aware with seeds 1–5. Parameters not changed in
a scenario inherit a single baseline. This avoids confounding every factor in one product.

- Deadlines: 50/100/200/300/500 ms, at 100 packets/s.
- Loads: 20/100/500 packets/s, 3 ms processing and capacity 8.
- Density: 10/20/30 nodes in the same 250 m square, reproducibly random.
- Channel: log-distance exponents 2.6/3.0/3.8; labels are parameter values, not assumed loss rates.
- Mobility: static, waypoint 5 m/s, waypoint 15 m/s, 20 nodes in a 250 m square.

The extended design uses seeds 1–10, 50 nodes and link-heavy/slack-heavy weights.
All these matrices are configurations, not claims that the extended study has run.
Actual commands and completed studies are listed in evidence/validation.md.

Use the packet summary and PHY trace to explain tradeoffs. If all protocols saturate
at 100% in a mild scenario, report that lack of discrimination. If a channel setting
disconnects the network, report zero delivery and null delay. Never discard such seeds.
