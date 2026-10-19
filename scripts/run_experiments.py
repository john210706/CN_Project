#!/usr/bin/env python3
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
import uuid
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.configuration import ROOT, load_config
from scripts.run_simulation import run
from analysis.load_results import discover
from analysis.aggregate import aggregate, comparisons
from analysis.plots import plots


def plan(path):
    matrix = yaml.safe_load(Path(path).read_text())
    if not isinstance(matrix, dict) or not {"scenarios", "protocols", "seeds"} <= set(
        matrix
    ):
        raise ValueError("Matrix needs scenarios, protocols, seeds")
    if len(set(matrix["seeds"])) != len(matrix["seeds"]):
        raise ValueError("Independent seed list cannot contain duplicates")
    jobs = []
    names = set()
    for scenario in matrix["scenarios"]:
        name = scenario["name"]
        if (
            not isinstance(name, str)
            or not name
            or any(not (c.isalnum() or c in "-_") for c in name)
            or name in names
        ):
            raise ValueError("Scenario names must be unique alphanumeric slugs")
        names.add(name)
        for protocol in matrix["protocols"]:
            for seed in matrix["seeds"]:
                c = load_config(
                    overrides={
                        **matrix.get("base", {}),
                        **scenario["settings"],
                        "protocol": protocol,
                        "seed": seed,
                    }
                )
                jobs.append((name, c))
    if not jobs:
        raise ValueError("Empty matrix")
    return jobs


def analyze(root, output):
    runs, errors = discover(root)
    if runs.empty:
        raise ValueError("No successful runs to analyze")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    stats = aggregate(runs)
    runs.to_csv(output / "runs.csv", index=False)
    stats.to_csv(output / "aggregate.csv", index=False)
    comparisons(stats).to_csv(output / "comparisons.csv", index=False)
    plots(runs, stats, output / "figures")
    (output / "analysis_warnings.json").write_text(json.dumps(errors, indent=2))
    return output


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--config", type=Path, default=ROOT / "config/experiment-matrix.yaml"
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--analyze", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    if a.analyze:
        print(analyze(a.analyze, a.output or ROOT / "results/processed"))
        return
    jobs = plan(a.config)
    if a.dry_run:
        for name, c in jobs:
            print(
                f"{name}: {c['protocol']}, seed={c['seed']}, nodes={c['nodes']}, rate={c['rate']}"
            )
        print(f"{len(jobs)} runs")
        return
    batch = (
        dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
        + "_"
        + uuid.uuid4().hex[:6]
    )
    root = a.output or ROOT / "results/raw" / batch
    root.mkdir(parents=True, exist_ok=False)
    (root / "matrix.yaml").write_text(a.config.read_text())
    failures = []
    for i, (name, c) in enumerate(jobs, 1):
        print(
            f"[{i}/{len(jobs)}] {name} / {c['protocol']} / seed {c['seed']}", flush=True
        )
        try:
            path, m = run(c, root)
            meta = json.loads((path / "run_metadata.json").read_text())
            meta.update(scenario=name, batch=batch)
            (path / "run_metadata.json").write_text(json.dumps(meta, indent=2))
            print(f"  DSDR {m['dsdr_pct']:.2f}%", flush=True)
        except Exception as e:
            failures.append({"scenario": name, "config": c, "error": str(e)})
            print(f"  FAILED: {e}", file=sys.stderr, flush=True)
    (root / "batch_failures.json").write_text(json.dumps(failures, indent=2))
    analyze(root, root / "analysis")
    print(root)
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
