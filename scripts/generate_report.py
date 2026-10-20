#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from scripts.configuration import ROOT
from analysis.load_results import discover
from analysis.aggregate import aggregate, comparisons


def table(frame, columns):
    out = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in frame[columns].itertuples(index=False, name=None):
        out.append(
            "| "
            + " | ".join(
                "—" if pd.isna(x) else f"{x:.2f}" if isinstance(x, float) else str(x)
                for x in row
            )
            + " |"
        )
    return "\n".join(out)


def generate(root, output):
    runs, errors = discover(root)
    batches = runs[runs.batch != "standalone"] if not runs.empty else runs
    stats = aggregate(batches)
    comparisons_frame = comparisons(stats)
    text = """# Deadline-Aware Opportunistic Routing for Wireless Networks
## Simulation-Based Study Using NS-3

### Abstract
This project studies whether receiver-side deadline feasibility can improve useful
packet delivery in an unreliable wireless network. Three C++ application-layer forwarding
strategies execute over the same NS-3.45 ad-hoc Wi-Fi/UDP transport: fixed next hop,
progress/link-based opportunistic forwarding, and deadline-aware opportunistic forwarding.
The proposed strategy combines normalized local link reception, geographic progress,
predicted slack and queue availability with cancellable forwarding timers. The accompanying
Python pipeline preserves packet-level evidence, independent-seed summaries and interactive
trace playback. Results below are read from successful simulation outputs; they are not
predictions or guarantees for deployed emergency communication.

### Introduction, problem and motivation
Packet delivery alone is insufficient when information loses value after a deadline.
An emergency message may arrive successfully yet too late to act upon. Wireless broadcast
also creates multiple possible relays, making the choice of which receiver forwards a
concrete opportunity to consider timeliness. The research question is whether using
remaining lifetime and estimated delivery delay improves deadline-satisfied delivery
relative to fixed and deadline-unaware forwarding under comparable conditions.

### Objectives
Implement real multi-hop wireless transmission, coordinate competing receivers, enforce
absolute packet deadlines, quantify delivery and overhead, and make every plotted outcome
traceable to actual simulator events. The hypothesis is conditional: deadline awareness
may help when candidate delays differ, but poor prediction can reject useful opportunities.

### Related work
Biswas and Morris's ExOR work selects relays after reception to exploit wireless diversity.
This project uses that broad receiver-opportunity idea, but does not reproduce ExOR's
batch coordination or MAC design. SPEED by He, Stankovic, Lu and Abdelzaher studies
soft real-time communication through geographic forwarding and delivery-speed control.
The present project's local slack score is an educational experimental design, not an
implementation of SPEED or a claim of a novel proven protocol. See the verified references.

### Architecture and implementation
The per-node C++ application owns a UDP socket, HELLO history, processing queue and packet
state. Every data hop traverses actual NS-3 Wi-Fi MAC/PHY models. A 76-byte serializable
header carries source/sequence identity, target, class, original creation/expiry, hop state
and positions. Python validates configurations, launches the compiled executable, derives
metrics from first destination arrival, aggregates seeds and renders figures. Streamlit
shows real topology samples, reception edges, candidate reasoning and outcomes.
See architecture.md for the network, lifecycle and pipeline diagrams.

### Proposed method
Let q be bounded HELLO reception quality, g normalized positive destination progress,
P local processing, Q reserved work and d distance to the initially configured target.
Predict D0=P+Q+ceil(d/range)*perHop. Normalize positive pre-contention slack and queue
availability, then score 0.3q+0.3g+0.3slack+0.1availability. Convert score to a bounded
holdoff and accept only when D0+holdoff+safety is strictly below remaining lifetime.
The node reserves a finite processing slot and schedules a forwarding event. It cancels
on an actual overheard downstream copy or expiry. It rechecks expiry immediately before
submitting to UDP. Basic opportunistic forwarding uses 0.5q+0.5g without deadline
eligibility. Fixed forwarding uses only the initial BFS next hop. Full equations and
state rules are in algorithm.md.

### Experimental setup and metrics
The radio is 802.11a at 5 GHz, 20 MHz, normally 6 Mbps and 30 dBm, with log-distance
attenuation and a 125 m maximum range. The primary design varies deadlines, offered
load, node density in a fixed square, path-loss exponent and waypoint motion separately.
All protocols share exogenous topology, traffic and mobility settings. Radio outcomes
need not remain paired because forwarding changes contention. Each primary scenario
uses five independent seeds. PDR counts unique deliveries, DSDR unique on-time deliveries,
and delay includes delivered packets only. Throughput counts delivered payload over full
simulation duration. Student-t 95% intervals use per-run outcomes, with sample size shown.
See methodology.md and metrics.md for definitions and censoring considerations.

### Measured results
"""
    if batches.empty:
        text += "No successful experiment batches were available when this report was generated. No performance improvement is claimed.\n"
    else:
        text += f"This report includes **{len(batches)} successful runs**, **{batches.scenario.nunique()} named scenarios**, and **{batches.batch.nunique()} batches**.\n\n"
        text += (
            table(
                stats,
                [
                    "scenario",
                    "protocol",
                    "dsdr_pct_mean",
                    "dsdr_pct_ci95",
                    "dsdr_pct_n",
                    "pdr_pct_mean",
                    "mean_delay_ms_mean",
                    "forwarding_transmissions_mean",
                ],
            )
            + "\n\n"
        )
        text += "### Differences against baselines\n\nPositive differences favor the proposed method; negative values are retained.\n\n"
        text += (
            table(
                comparisons_frame,
                [
                    "scenario",
                    "baseline",
                    "dsdr_difference_pp",
                    "dsdr_relative_change_pct",
                ],
            )
            + "\n\n"
        )
        for baseline, g in comparisons_frame.groupby("baseline"):
            better = int((g.dsdr_difference_pp > 1e-9).sum())
            worse = int((g.dsdr_difference_pp < -1e-9).sum())
            equal = len(g) - better - worse
            text += f"Against {baseline}, the proposed method has a higher observed mean in {better} scenario/batch comparisons, a lower mean in {worse}, and an equal mean in {equal}. These counts are descriptive, not significance tests.\n\n"
        basic = comparisons_frame[comparisons_frame.baseline == "opportunistic"]
        if not basic.empty and (basic.dsdr_difference_pp <= 1e-9).all():
            text += "The executed matrix does **not support a general DSDR advantage over basic opportunistic forwarding**: no scenario has a higher proposed mean. Distinct candidate decisions are verified, but that mechanism alone is insufficient evidence of better end-to-end performance.\n\n"
        load = stats[stats.scenario == "load-500"]
        if not load.empty:
            text += (
                "At 500 packets/s/flow, observed mean DSDR is "
                + ", ".join(
                    f"{row.protocol}: {row.dsdr_pct_mean:.2f}%"
                    for row in load.itertuples()
                )
                + ". This stress case favors the fixed baseline in the tested connected topology.\n\n"
            )
        text += "### Source provenance and figures\n\n"
        for batch, group in batches.groupby("batch"):
            folder = Path(group.iloc[0].path).parent
            relative = Path("..") / folder.relative_to(ROOT)
            text += f"- Batch `{batch}`: {len(group)} runs. [Run manifest]({relative}/analysis/runs.csv), [aggregate table]({relative}/analysis/aggregate.csv).\n"
            for figure in [
                "load-500_dsdr_pct.svg",
                "sensitivity_deadline.svg",
                "sensitivity_rate.svg",
                "sensitivity_nodes.svg",
                "sensitivity_pathLoss.svg",
                "sensitivity_speed.svg",
            ]:
                if (folder / "analysis/figures" / figure).exists():
                    text += f"\n![Measured {figure}]({relative}/analysis/figures/{figure})\n"
        text += "\n"
    text += """### Discussion
A higher DSDR accompanied by lower PDR can reflect deliberate rejection of predicted
late packets. Lower delivered-only delay may partly reflect this selection. Extra relays
increase overhead even when they deliver useful packets. Low-loss, lightly loaded cases
can leave little room for improvement. Dense networks can improve reception diversity
but also create more contention and hidden-terminal competition. Weak channels or stale
locations can disconnect the available greedy paths. No zero-delivery run is removed.

### Limitations and future work
The baseline is application-level fixed forwarding over broadcast, not AODV/OLSR. Target
locations are initially configured and can become stale. Greedy progress has no void
recovery. The downstream predictor is approximate; HELLOs are smaller than data packets.
Cancellation does not reclaim committed processing work or remove packets already queued
inside Wi-Fi. Hidden receivers cannot suppress one another reliably. Short five-seed
replications are insufficient for deployment or universal significance claims. Future
work should compare adaptive delay estimators, refreshed location announcements,
longer experiments, realistic obstacles/fading, and an additional standard IP-routing baseline.

### Conclusion
The artifact provides an executable experimental test of deadline-aware receiver selection
and a reproducible route from Wi-Fi events to measured metrics, plots and inspection.
The observed results apply to the recorded scenarios and modeling assumptions. They do
not establish that deadline-aware forwarding always wins or guarantees emergency delivery.

### References
1. NS-3.45 official installation guide: https://www.nsnam.org/docs/release/3.45/installation/html/overview.html
2. NS-3.45 official source mirror: https://github.com/nsnam/ns-3-dev-git/tree/ns-3.45
3. S. Biswas and R. Morris, ExOR: Opportunistic Multi-Hop Routing for Wireless Networks,
   ACM SIGCOMM 2005. Official program: https://conferences.sigcomm.org/sigcomm/2005/techprog.html
4. T. He, J. Stankovic, C. Lu and T. Abdelzaher, SPEED: A Stateless Protocol for Real-Time
   Communication in Sensor Networks, ICDCS 2003. Author publication record:
   https://www.cs.virginia.edu/~stankovic/sensornet.html
"""
    text += f"\n### Data loading warnings\n\n{len(errors)} failed/unavailable records found.\n"
    if errors:
        text += "\n".join("- " + e for e in errors) + "\n"
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(text)
    print(output)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT / "results/raw")
    p.add_argument("--output", type=Path, default=ROOT / "docs/final-report.md")
    a = p.parse_args()
    generate(a.root, a.output)


if __name__ == "__main__":
    main()
