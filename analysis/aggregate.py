import numpy as np
import pandas as pd
from scipy.stats import t

METRICS = [
    "pdr_pct",
    "dsdr_pct",
    "mean_delay_ms",
    "throughput_kbps",
    "unique_expired",
    "forwarding_transmissions",
    "duplicate_transmissions",
]


def aggregate(runs):
    rows = []
    if runs.empty:
        return pd.DataFrame()
    # Only explicitly named batch scenarios are aggregated; standalone data are kept separate by path.
    runs = runs.copy()
    if (runs.batch == "standalone").any():
        runs.loc[runs.batch == "standalone", "scenario"] = runs.loc[
            runs.batch == "standalone", "path"
        ]
    for keys, group in runs.groupby(["batch", "scenario", "protocol"]):
        row = dict(zip(["batch", "scenario", "protocol"], keys))
        for metric in METRICS:
            values = group[metric].dropna().astype(float)
            n = len(values)
            mean = float(values.mean()) if n else np.nan
            sd = float(values.std(ddof=1)) if n > 1 else np.nan
            half = float(t.ppf(0.975, n - 1) * sd / np.sqrt(n)) if n > 1 else np.nan
            row.update(
                {
                    metric + "_mean": mean,
                    metric + "_sd": sd,
                    metric + "_ci95": half,
                    metric + "_n": n,
                }
            )
        rows.append(row)
    return pd.DataFrame(rows)


def comparisons(stats):
    rows = []
    if stats.empty:
        return pd.DataFrame()
    for keys, g in stats.groupby(["batch", "scenario"]):
        by = g.set_index("protocol")
        if "deadline_aware" not in by.index:
            continue
        proposed = by.loc["deadline_aware", "dsdr_pct_mean"]
        for base in ["fixed", "opportunistic"]:
            if base not in by.index:
                continue
            value = by.loc[base, "dsdr_pct_mean"]
            rows.append(
                {
                    "batch": keys[0],
                    "scenario": keys[1],
                    "baseline": base,
                    "dsdr_difference_pp": proposed - value,
                    "dsdr_relative_change_pct": 100 * (proposed - value) / value
                    if value
                    else None,
                }
            )
    return pd.DataFrame(rows)
