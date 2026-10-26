#!/usr/bin/env python3
"""Run the live assignment demo, print useful results, then open NetAnim."""

import argparse
import csv
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.configuration import ROOT, load_config
from scripts.run_simulation import run


def first_packet_route(run_dir: Path) -> str:
    with (run_dir / "packet_events.csv").open(newline="") as source:
        rows = list(csv.DictReader(source))
    packet_ids = [
        row["packet_id"]
        for row in rows
        if row["event_type"] == "PACKET_CREATED" and row["packet_id"]
    ]
    if not packet_ids:
        return "No packet route recorded"
    packet_id = packet_ids[0]
    packet_rows = [row for row in rows if row["packet_id"] == packet_id]
    hops = [
        int(row["current_node_id"])
        for row in packet_rows
        if row["event_type"] == "PACKET_TX"
    ]
    deliveries = [
        int(row["current_node_id"])
        for row in packet_rows
        if row["event_type"] == "DESTINATION_DELIVERED"
    ]
    if deliveries and (not hops or hops[-1] != deliveries[0]):
        hops.append(deliveries[0])
    return " → ".join(f"Node {node}" for node in hops)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the live NS-3 and NetAnim demo")
    parser.add_argument("--config", type=Path, default=ROOT / "config/diamond.yaml")
    parser.add_argument("--no-viewer", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    print("\n" + "=" * 64)
    print(" DEADLINE-AWARE OPPORTUNISTIC ROUTING — LIVE NS-3 DEMO")
    print("=" * 64)
    print(f" Protocol       : {config['protocol']}")
    print(f" Topology       : {config['topology']}")
    print(f" Nodes          : {config['nodes']}")
    print(f" Mobility       : {config['mobility']}")
    print(f" Packet rate    : {config['rate']} packets/second")
    print(f" Deadline       : {config['deadline']} ms")
    print("\nRunning the real NS-3 Wi-Fi simulation...", flush=True)

    started = time.monotonic()
    run_dir, metrics = run(config)
    elapsed = time.monotonic() - started

    print("\n" + "-" * 64)
    print(" SIMULATION RESULTS")
    print("-" * 64)
    print(f" Generated packets      : {metrics['generated']}")
    print(f" Delivered packets      : {metrics['unique_delivered']}")
    print(f" Delivered on time      : {metrics['on_time_delivered']}")
    print(f" Packet delivery ratio  : {metrics['pdr_pct']:.2f}%")
    print(f" Deadline success ratio : {metrics['dsdr_pct']:.2f}%")
    print(f" Mean delay             : {metrics['mean_delay_ms']:.2f} ms")
    print(f" Mean hops              : {metrics['mean_hops']:.2f}")
    print(f" PHY transmissions      : {metrics['phy_transmissions']}")
    print(f" Example packet route   : {first_packet_route(run_dir)}")
    print(f" Real execution time    : {elapsed:.2f} seconds")
    print(f"\nResult folder: {run_dir}")
    print(f"NetAnim file : {run_dir / 'animation.xml'}")

    if args.no_viewer:
        return
    print("\nOpening NetAnim. Select animation.xml, click R, set the speed")
    print("toward Slow, and press Play. Close NetAnim to return here.\n", flush=True)
    subprocess.run(
        ["bash", str(ROOT / "scripts/launch_netanim.sh"), str(run_dir / "animation.xml")],
        cwd=ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
