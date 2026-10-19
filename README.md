# Deadline-Aware Opportunistic Routing for Wireless Networks

A reproducible NS-3.45 study of **timely delivery**, with a Streamlit trace explorer.
The project implements three application-layer forwarding strategies over the **same
real ad-hoc Wi-Fi/UDP broadcast transport**. It does not implement AODV, replace the
radio with Python, or presume that the proposed algorithm wins.

| Mode | Decision |
|---|---|
| `fixed` | Initial geometric BFS next hop; only the addressed relay may forward |
| `opportunistic` | Receiver competition using local beacon reception and geographic progress |
| `deadline_aware` | Receiver competition with predicted slack, queue availability, feasibility and expiry cancellation |

## Quick start

Linux x86_64, network access and several GB free disk are needed for first setup.
No sudo is used. Missing build tools are installed in `.tools/env` using conda-forge;
Python packages are installed in `.venv`. Upstream NS-3 stays under ignored `vendor/`.

```bash
bash scripts/setup.sh
source scripts/env.sh  # add the isolated toolchain to this terminal
make test
make demo
make dashboard
```

Open [the local dashboard](http://localhost:8501). It can launch NS-3 and explore existing
runs, actual receptions, candidate decisions and protocol comparisons.

If tools are already installed, setup uses them. To use another NS-3.45 source checkout:

```bash
export NS3_DIR=/absolute/path/to/ns-3.45
bash scripts/setup.sh
```

The build script creates a checked symlink at `NS3_DIR/scratch/deadline-routing` and
refuses to replace unrelated content. Other NS-3 releases are not claimed compatible.
Use `BUILD_JOBS=1 bash scripts/build.sh` on memory-constrained machines.

## Run and compare

```bash
.venv/bin/python scripts/run_simulation.py --config config/diamond.yaml
.venv/bin/python scripts/run_simulation.py --protocol fixed --nodes 20 --topology grid --seed 42
.venv/bin/python scripts/run_demos.py --demo multihop
.venv/bin/python scripts/run_experiments.py --config config/experiment-matrix.yaml --dry-run
make experiment
.venv/bin/python scripts/validate_results.py results/raw
make report
```

The primary matrix has 255 runs: 17 separate scenarios × 3 protocols × 5 seeds.
It varies deadline, load, density, channel exponent and mobility without creating a
Cartesian product of all dimensions. The extended matrix uses ten seeds, 50 nodes
and two weight settings. Experiments can take several minutes and generate many MB
of traces. Each run gets a unique directory; failures retain logs and are reported.

Configurations overlay `config/default.yaml`. All supported simulator options are
exposed through YAML and `--PrintHelp` on the compiled binary. `pairs: [[0,9],[1,8]]`
sets arbitrary concurrent flows; otherwise sources 0…flows−1 send to the last node.
`deadline: 0` uses emergency/video/data/background lifetimes 50/100/500/1000 ms.
`traffic: poisson` enables exponential interarrivals with independent RNG streams.

## Outputs

Each `results/raw/<run>/` contains:

- `run_metadata.json`: exact arguments, complete configuration, version and status.
- `packet_events.csv`: received data, candidates, timers, UDP sends and delivery.
- `radio_events.csv`: actual PHY transmission starts and reception failure events.
- `node_positions.csv`: sampled NS-3 mobility positions.
- `packet_summary.csv`: one row per generated packet, first delivery and deadline outcome.
- `metrics.json` / `metrics.csv`: global metrics plus per-class and per-flow results.
- `stdout.log` / `stderr.log`: simulator diagnostics.

Batch directories also contain the input matrix, failure ledger, aggregate tables,
percentage-point comparisons, and PNG/SVG figures under `analysis/figures/`.
`docs/final-report.md` is generated from actual successful batch records.

PDR and DSDR use unique generated packets as denominator. Delay distributions include
only delivered packets. Throughput uses the full configured simulation interval,
including warmup and drain. A local drop is an event, not necessarily final packet loss.

## Source map

- `simulation/`: serialized wire header, selection model, forwarding app and Wi-Fi setup.
- `scripts/`: setup, safe launcher, experiment runner, validation, demos and report generation.
- `analysis/`: event-derived metrics, result loader, t confidence intervals and plots.
- `dashboard/`: Streamlit/Plotly run controls, playback and evidence inspection.
- `tests/`: C++ self-tests invoked through pytest, Python tests and real radio integration tests.
- `docs/`: algorithm, methodology, architecture, report, presentation and viva material.
- `evidence/validation.md`: commands and results actually checked on this machine.

## Modeling limits

The fixed baseline is application forwarding over broadcast, not IP routing. Destination
coordinates are initial mission configuration; mobile destinations can make them stale.
Opportunistic nodes use their own positions and the sender coordinates carried on the
wire, not other nodes' live state. Greedy progress can stall at geographic voids.
Beacon reception is an incoming-link estimate; downstream delay is a simple prediction.
Timer suppression depends on actual overhearing and can fail with hidden terminals.
The radio combines log-distance attenuation with an explicit maximum range cutoff.
There is no guarantee for real emergency networks or for arbitrary topologies.
See [limitations](docs/limitations.md), [algorithm](docs/algorithm.md), and
[validation evidence](evidence/validation.md) before making research claims.

## References

- [NS-3.45 installation guide](https://www.nsnam.org/docs/release/3.45/installation/html/overview.html)
- [Pinned official source mirror](https://github.com/nsnam/ns-3-dev-git/tree/ns-3.45)
- [Biswas and Morris, ExOR, SIGCOMM 2005](https://conferences.sigcomm.org/sigcomm/2005/techprog.html)
- [He et al., SPEED publications](https://www.cs.virginia.edu/~stankovic/sensornet.html)
# CN_Project
