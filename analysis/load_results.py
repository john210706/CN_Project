import json
from pathlib import Path
import pandas as pd
from analysis.metrics import read_events


def discover(root):
    rows = []
    errors = []
    for meta in sorted(Path(root).rglob("run_metadata.json")):
        try:
            m = json.loads(meta.read_text())
            if not isinstance(m, dict):
                raise ValueError("Metadata must be an object")
            if m.get("status") != "success":
                errors.append(
                    f"{meta.parent.name}: {m.get('status', 'unknown')} {m.get('error', '')}"
                )
                continue
            metrics = json.loads((meta.parent / "metrics.json").read_text())
            if not isinstance(metrics, dict):
                raise ValueError("Metrics must be an object")
            c = m["config"]
            if not isinstance(c, dict):
                raise ValueError("Configuration must be an object")
            rows.append(
                {
                    "path": str(meta.parent),
                    **{k: v for k, v in c.items() if not isinstance(v, list)},
                    **{k: v for k, v in metrics.items() if not isinstance(v, list)},
                    "scenario": m.get("scenario", c["topology"]),
                    "batch": m.get("batch", "standalone"),
                }
            )
        except (OSError, ValueError, KeyError, TypeError) as e:
            errors.append(f"{meta.parent.name}: {e}")
    return pd.DataFrame(rows), errors


def load_run(path):
    path = Path(path)
    metadata = json.loads((path / "run_metadata.json").read_text())
    if not isinstance(metadata, dict) or metadata.get("status") != "success":
        raise ValueError("Run is not successful")
    events = read_events(path / "packet_events.csv")
    positions = pd.read_csv(path / "node_positions.csv")
    if not {"simulation_time_ms", "node_id", "x", "y", "z"} <= set(positions):
        raise ValueError("Invalid node positions schema")
    if positions.empty:
        raise ValueError("No recorded node positions")
    summary = pd.read_csv(path / "packet_summary.csv")
    metrics = json.loads((path / "metrics.json").read_text())
    required_metrics = {
        "generated",
        "unique_delivered",
        "on_time_delivered",
        "late_delivered",
        "undelivered",
        "pdr_pct",
        "dsdr_pct",
        "mean_delay_ms",
        "forwarding_transmissions",
        "duplicate_transmissions",
        "duplicate_suppressions",
        "unique_expired",
        "queue_drops",
        "phy_transmissions",
        "phy_rx_drop_events",
        "per_class",
        "per_flow",
    }
    if not isinstance(metrics, dict) or not required_metrics <= set(metrics):
        raise ValueError("Incomplete metrics schema")
    if not {"packet_id", "delay_ms", "on_time", "delivered"} <= set(summary):
        raise ValueError("Incomplete packet summary schema")
    if not {"protocol", "topology", "nodes", "seed", "run"} <= set(
        metadata.get("config", {})
    ):
        raise ValueError("Incomplete configuration metadata")
    return metadata, events, positions, summary, metrics
