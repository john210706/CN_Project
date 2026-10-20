# Validation evidence

Recorded on 2026-10-20T03:24:27.660828+00:00.
All results below were executed locally. No simulation values were fabricated.

## Environment and build

- Host: Fedora Linux 44, Linux x86_64; original system Python 3.14.7.
- Initial machine had no C++ compiler, CMake, Make or NS-3.
- Isolated project toolchain: GCC 15.3.0 (conda-forge), CMake 4.4.4, Ninja and Make 4.4.1.
- Analysis interpreter: Python 3.12.15 in `.venv`.
- NS-3: release 3.45, official mirror tag commit `4059af204636298c061df368e241941fa3ff97bf`.
- C++ standard: C++20 selected by NS-3.45; release build, assertions disabled upstream.
  Project self-tests use explicit exceptions and remain active in release builds.
- Binary SHA-256 after final build: `8488e799c1e59946b3fb3b174dfbd3dd3bc2a0c0e0120a8517c63199622af2cd`.
- Exact toolchain package URLs: `toolchain-linux-64.lock`; Python versions: `python-lock.txt`.
- Project source digests: `source-sha256.json`. Git was initialized; no initial commit or remote push was made.

Commands actually run:

```bash
bash scripts/setup.sh
bash scripts/build.sh
source scripts/env.sh
make test
make demo
.venv/bin/python scripts/run_experiments.py --config config/experiment-matrix.yaml
.venv/bin/python scripts/run_experiments.py --config config/supplemental-matrix.yaml
.venv/bin/python scripts/validate_results.py results/raw
make report
bash scripts/launch_dashboard.sh
```

NS-3 configuration/build invoked by the build script:

```bash
python3 ns3 configure --build-profile=release --enable-modules=core,network,internet,wifi,mobility --disable-examples --disable-tests -- -G Ninja
python3 ns3 build deadline-routing -j 2
```

Build and setup succeeded. The actual CMake target is
`scratch_deadline-routing_deadline-routing`, producing
`vendor/ns-3.45/build/scratch/deadline-routing/ns3.45-deadline-routing`.
The full stdout records are `build-output.txt` and `setup-output.txt`.

## Automated verification

- **35 pytest tests passed**, including real compiled simulator executions.
- **329 successful run directories validated** by independent trace-to-metric recomputation;
  zero unavailable or failed records in `results/raw` at the audit.
- Ruff check of scripts, analysis, dashboard and tests: all checks passed.
- Matplotlib emitted 14 upstream Pyparsing deprecation warnings; no failed tests.
- C++ self-test passed: wire-size/serialization, integer times and identity, invalid headers,
  deadline feasibility, bounded score preference, deadline-independent baseline and weights.
- Real Wi-Fi tests passed: multiple receivers, fixed and opportunistic multi-hop delivery,
  duplicate suppression backed by an actual reception, expiry without data transmission,
  reproducible event/position files, channel degradation and mobility disconnection.
- Finite queue overflow, hop limit, Poisson multi-flow identity and random-waypoint motion passed.
- Hidden-node test: visible candidates suppress; separated candidates produce extra forwards.
- Candidate-choice test: packet 7 uses node 1 in basic mode and node 2 in deadline-aware mode;
  node 1's measured incoming link estimate is higher, but its delay is infeasible under the
  configured policy. The controlled demo explicitly enables receiver fault injection.
- Streamlit AppTest passed with actual stored runs. Missing/malformed data and configuration
  checks passed, including incomplete metrics and non-object metadata.

See `test-output.txt`, `result-validation.txt`, and extracted packet-7 CSVs for evidence.

## Executed demonstrations

`make demo` executed all eight demonstrations (ten runs because deadline selection compares
three protocols). The latest exact paths and DSDRs are in `demo-output.txt` and
`results/reports/demos.json`.

- Two-node wireless, multiple receivers, duplicate suppression and multihop delivered packets.
- The 0.2 ms expiration demo produced zero data sends and cancelled source queue timers.
- The congestion demo generated queue overflow and measured throughput/delivery changes.
- The high-speed velocity demo moved the actual radio nodes and disconnected the path;
  zero delivery is the observed result, not an execution failure.
- The lossy candidate-selection demo does not establish improvement: deadline-aware DSDR
  was 93.33%, while fixed and basic opportunistic were 100% for this seed.

The dashboard was launched in a real browser. Clicking **Run NS-3** completed a run,
showed 60/60 on-time packets in the chosen diamond configuration, and loaded its traces.
The playback Play button advanced to **DESTINATION_DELIVERED**, drawing only the recorded
reception edges. A screenshot inspection checked the layout and real node positions.
Streamlit is local-only at `127.0.0.1:8501`; it can be restarted with the launch script.

## Executed studies and generated artifacts

- Primary: `results/raw/20261019T192805_cab57b` — 255 runs, 17 scenarios, three protocols, five seeds.
- Supplemental: `results/raw/20261019T192957_45fe78` — 45 runs: 50-node density and two weight settings.
- Both batches have an empty `batch_failures.json` and per-run configuration/command records.
- Figure counts: {'primary': {'png': 140, 'svg': 140}, 'supplemental': {'png': 25, 'svg': 25}}. PNG and SVG exports were generated from these runs.
- `analysis/runs.csv`, `analysis/aggregate.csv`, `analysis/comparisons.csv` accompany each batch.
- Copies of these tables and selected figures are retained in `evidence/` for review.
- `docs/final-report.md` includes actual results, negative findings, provenance and figures.
- The ten-seed extended matrix is supplied but was **not executed in full**.

At load 500 packets/s/flow, mean DSDR was deadline-aware 62.40%, basic opportunistic
63.36%, fixed 65.15%. Across the 20 named scenarios, deadline-aware exceeded the fixed
mean in three, fell below it in one and tied in 16. It exceeded basic opportunistic in
zero, fell below it in one and tied in 19. These are descriptive comparisons; no universal
advantage or significance claim is made.

## Calibration and resolved failures

Initial 16 dBm radio runs failed delivery tests because the chosen distances were below
NS-3's default -82 dBm preamble threshold. Those debugging runs remain in `results/debug`.
A 26 dBm pilot built and ran, but exposed weak diagonal grid links inside the geometric
BFS cutoff. Its complete 255-run outputs are retained under
`results/pilot/20261019T192613_58f280` and are excluded from the final study.
The connected baseline was set to 30 dBm for **all protocols**, with the same real channel
models. The deliberately unfavorable exponent 3.8 scenario retains its zero-delivery result.

Formatting revealed a missing direct `<cstdint>` include in the configuration header.
It was fixed, rebuilt successfully, and followed by the full passing test suite.

## Limits and explicit deviations

- Application-layer fixed-next-hop baseline, not AODV or an IP routing implementation.
- Initial target locations, greedy progress and approximate downstream delay remain assumptions.
- Wi-Fi channel width is fixed at 20 MHz for valid 802.11a operation; data rate, power,
  path-loss exponent and range are configurable.
- App expiry cannot retract packets already submitted to the MAC queue; PHY airtime is
  separately logged from socket-accepted sends.
- Processing reservations are not reclaimed on suppression; this is documented committed work.
- Short five-seed studies do not establish steady-state or real-world guarantees.
- No privileged system changes, external publication, remote pushes, account changes,
  or public deployment were performed.
