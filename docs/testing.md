# Testing

Run `make test` after `make build`. Python tests validate malformed configurations,
identity accounting, inclusive deadline boundaries, duplicate deliveries, undefined
metrics, missing files and Student-t aggregation. A C++ self-test exercises the real
NS-3 Header serialization plus scoring and feasibility functions.

Integration tests execute the compiled NS-3 program. They inspect actual events for
Wi-Fi reception, multiple receivers, multi-hop fixed forwarding, opportunistic suppression,
deadline-aware infeasibility, queued expiry without transmission, identical seeded traces,
channel degradation, mobility disconnection and load-induced queue overflow.
Dashboard tests use Streamlit AppTest. `scripts/validate_results.py` independently
recomputes metrics from every successful run and checks expired sends and hop limits.

A unit test of the scoring function is not proof that the radio works. Radio integration
tests require the real executable and fail if it is unavailable. See the separate validation
evidence for exact results actually executed in the delivered environment.
