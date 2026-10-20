#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.configuration import ROOT, load_config
from scripts.run_simulation import run

DEMOS = {
    "wireless": dict(topology="line", nodes=2, spacing=60),
    "broadcast": dict(topology="diamond", nodes=4, protocol="opportunistic"),
    "suppression": dict(
        topology="diamond", nodes=4, protocol="opportunistic", slowProcessing=15
    ),
    "deadline": dict(
        topology="diamond",
        nodes=4,
        deadline=25,
        slowProcessing=6,
        maxHoldoff=80,
        rate=5,
        weights=[0.2, 0.2, 0.5, 0.1],
        lossNode=2,
        loss=0.1,
    ),
    "expiration": dict(topology="diamond", nodes=4, deadline=0.2, processing=5),
    "multihop": dict(topology="line", nodes=5),
    "congestion": dict(
        topology="grid", nodes=10, rate=500, flows=3, processing=5, queueCapacity=4
    ),
    "mobility": dict(topology="line", nodes=5, mobility="velocity", speed=50),
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--demo", choices=list(DEMOS))
    a = p.parse_args()
    results = []
    for name, settings in DEMOS.items():
        if a.demo and a.demo != name:
            continue
        configs = [settings]
        if name == "deadline":
            configs = [
                {**settings, "protocol": p}
                for p in ["fixed", "opportunistic", "deadline_aware"]
            ]
        for conf in configs:
            path, m = run(load_config(overrides=conf))
            meta_path = path / "run_metadata.json"
            metadata = json.loads(meta_path.read_text())
            metadata["demo"] = name
            meta_path.write_text(json.dumps(metadata, indent=2))
            results.append({"demo": name, "path": str(path), "metrics": m})
            print(name, path, f"DSDR={m['dsdr_pct']:.2f}%")
    dest = ROOT / "results/reports/demos.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
