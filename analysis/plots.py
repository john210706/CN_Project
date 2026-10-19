from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import t
from analysis.aggregate import METRICS

COLORS = {"fixed": "#3b82f6", "opportunistic": "#e5a028", "deadline_aware": "#009e82"}
LABELS = {
    "pdr_pct": "Packet delivery (%)",
    "dsdr_pct": "On-time delivery (%)",
    "mean_delay_ms": "Mean delay (ms)",
    "throughput_kbps": "Useful throughput (kbps)",
    "unique_expired": "Unique packets with expiration events",
    "forwarding_transmissions": "Forwarding transmissions",
    "duplicate_transmissions": "Redundant same-depth transmissions",
}


def save(fig, path):
    fig.tight_layout()
    fig.savefig(path.with_suffix(".png"), dpi=180)
    fig.savefig(path.with_suffix(".svg"))
    plt.close(fig)


def plots(runs, stats, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {"font.size": 10, "axes.spines.top": False, "axes.spines.right": False}
    )
    for (batch, scenario), g in stats.groupby(["batch", "scenario"]):
        slug = "".join(c if c.isalnum() or c == "-" else "_" for c in scenario)[-90:]
        for metric in METRICS:
            fig, ax = plt.subplots(figsize=(6.5, 4))
            ax.bar(
                g.protocol,
                g[metric + "_mean"],
                color=[COLORS[p] for p in g.protocol],
                yerr=g[metric + "_ci95"].fillna(0),
                capsize=4,
            )
            ax.set(
                title=f"{scenario}: {LABELS[metric]}",
                ylabel=LABELS[metric],
                xlabel="Forwarding protocol",
            )
            save(fig, output / f"{slug}_{metric}")
    for dimension, label, prefix in [
        ("deadline", "Deadline (ms)", "deadline-"),
        ("rate", "Traffic (packets/s/flow)", "load-"),
        ("nodes", "Node count (fixed area)", "density-"),
        ("pathLoss", "Path-loss exponent", "channel-"),
        ("speed", "Mobility speed (m/s)", "mobility-"),
    ]:
        data = runs[runs.scenario.str.startswith(prefix)]
        if data.empty:
            continue
        fig, ax = plt.subplots(figsize=(6.5, 4))
        for protocol, g in data.groupby("protocol"):
            z = g.groupby(dimension).dsdr_pct.agg(["mean", "std", "count"]).sort_index()
            ci = z["std"] * z["count"].map(
                lambda n: t.ppf(0.975, n - 1) / np.sqrt(n) if n > 1 else 0
            )
            ax.errorbar(
                z.index,
                z["mean"],
                yerr=ci.fillna(0),
                marker="o",
                label=protocol,
                color=COLORS[protocol],
                capsize=3,
            )
        ax.set(title="Deadline-satisfied delivery", xlabel=label, ylabel="DSDR (%)")
        ax.legend()
        save(fig, output / f"sensitivity_{dimension}")
    # ECDFs are grouped by scenario to avoid mixing incompatible experiments.
    for scenario, g in runs.groupby("scenario"):
        if g.batch.eq("standalone").all():
            continue
        fig, ax = plt.subplots(figsize=(6.5, 4))
        plotted = False
        for protocol, rows in g.groupby("protocol"):
            values = []
            for p in rows.path:
                values.extend(
                    pd.read_csv(Path(p) / "packet_summary.csv").delay_ms.dropna()
                )
            if values:
                values = np.sort(values)
                ax.step(
                    values,
                    np.arange(1, len(values) + 1) / len(values),
                    where="post",
                    label=protocol,
                    color=COLORS[protocol],
                )
                plotted = True
        if plotted:
            ax.set(
                title=f"{scenario}: delivered-packet delay distribution",
                xlabel="End-to-end delay (ms)",
                ylabel="Empirical cumulative probability",
            )
            ax.legend()
            save(fig, output / f"{scenario}_delay_distribution")
        else:
            plt.close(fig)
