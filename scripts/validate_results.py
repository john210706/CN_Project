#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.metrics import read_events, summarize, metrics
from analysis.load_results import discover


def validate_run(path):
    path = Path(path)
    meta = json.loads((path / "run_metadata.json").read_text())
    c = meta["config"]
    e = read_events(path / "packet_events.csv")
    s = summarize(e)
    m = metrics(s, e, c["duration"])
    stored = json.loads((path / "metrics.json").read_text())
    for k, v in m.items():
        if v != stored[k]:
            raise ValueError(f"{path}: mismatched metric {k}")
    if (
        c["protocol"] == "deadline_aware"
        and (e.loc[e.event_type == "PACKET_TX", "remaining_time_ms"] <= 0).any()
    ):
        raise ValueError("Expired application transmission")
    if (
        e.loc[e.event_type == "DESTINATION_DELIVERED", "hop_count"] > c["maxHops"]
    ).any():
        raise ValueError("Hop limit exceeded")
    return m


def main():
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path, nargs="?", default=Path("results/raw"))
    a = p.parse_args()
    runs, errors = discover(a.root)
    for path in runs.get("path", []):
        validate_run(path)
    print(
        f"Validated {len(runs)} successful runs; {len(errors)} unavailable/failed runs"
    )
    if errors:
        print("\n".join(errors))
        sys.exit(1)


if __name__ == "__main__":
    main()
