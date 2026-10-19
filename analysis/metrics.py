import json
from pathlib import Path
import numpy as np
import pandas as pd

EVENT_COLUMNS = {
    "simulation_time_ms",
    "event_type",
    "packet_id",
    "source_id",
    "destination_id",
    "current_node_id",
    "creation_time_ms",
    "expiry_time_ms",
    "hop_count",
    "payload_bytes",
    "drop_reason",
    "traffic_class",
    "previous_forwarder_id",
    "remaining_time_ms",
    "candidate_score",
    "estimated_remaining_delay_ms",
    "forwarding_wait_ms",
    "queue_delay_ms",
    "link_quality",
    "normalized_progress",
    "slack_ms",
}


def read_events(path):
    data = pd.read_csv(path, keep_default_na=False)
    missing = EVENT_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Missing event columns: {sorted(missing)}")
    for col in EVENT_COLUMNS - {"event_type", "drop_reason"}:
        data[col] = pd.to_numeric(data[col], errors="raise")
        if not np.isfinite(data[col]).all():
            raise ValueError(f"Nonfinite {col}")
    return data


def summarize(events):
    created = events[events.event_type == "PACKET_CREATED"].copy()
    if created.packet_id.duplicated().any():
        raise ValueError("Duplicate generated packet identities")
    arrivals = (
        events[events.event_type == "DESTINATION_DELIVERED"]
        .sort_values("simulation_time_ms")
        .drop_duplicates("packet_id")
    )
    if not set(arrivals.packet_id) <= set(created.packet_id):
        raise ValueError("Delivery without generation")
    if not (arrivals.current_node_id == arrivals.destination_id).all():
        raise ValueError("Packet delivered to wrong destination")
    summary = created[
        [
            "packet_id",
            "source_id",
            "destination_id",
            "traffic_class",
            "creation_time_ms",
            "expiry_time_ms",
            "payload_bytes",
        ]
    ].copy()
    summary = summary.merge(
        arrivals[["packet_id", "simulation_time_ms", "hop_count"]].rename(
            columns={"simulation_time_ms": "first_arrival_ms"}
        ),
        on="packet_id",
        how="left",
    )
    summary["delivered"] = summary.first_arrival_ms.notna()
    summary["on_time"] = summary.delivered & (
        summary.first_arrival_ms <= summary.expiry_time_ms
    )
    summary["delay_ms"] = summary.first_arrival_ms - summary.creation_time_ms
    if (summary.delay_ms.dropna() < 0).any():
        raise ValueError("Arrival precedes generation")
    reasons = (
        events[
            (events.event_type.isin(["PACKET_DROPPED", "PACKET_EXPIRED"]))
            & ~events.drop_reason.isin(["DUPLICATE", "NO_PROGRESS"])
        ]
        .groupby("packet_id")
        .drop_reason.agg(lambda s: "|".join(sorted(set(s))))
    )
    summary["observed_drop_reasons"] = summary.packet_id.map(reasons).fillna("")
    summary["terminal_status"] = np.where(
        summary.on_time,
        "DELIVERED_ON_TIME",
        np.where(summary.delivered, "DELIVERED_LATE", "UNDELIVERED_AT_STOP"),
    )
    return summary


def metrics(summary, events, duration):
    n = len(summary)
    delivered = summary[summary.delivered]
    ontime = summary[summary.on_time]
    tx = events[events.event_type == "PACKET_TX"]
    forwarded = tx[tx.current_node_id != tx.source_id]
    # Extra relays at the same hop depth count as redundant transmissions, including hidden-terminal branches.
    duplicates = int(tx.duplicated(["packet_id", "hop_count"]).sum())
    expiry = events[events.event_type == "PACKET_EXPIRED"]

    def avg(s):
        return float(s.mean()) if len(s) else None

    def ratio(count):
        return float(100 * count / n) if n else 0.0

    delay = delivered.delay_ms
    result = dict(
        generated=n,
        unique_delivered=len(delivered),
        on_time_delivered=len(ontime),
        late_delivered=len(delivered) - len(ontime),
        deadline_missed=int(
            ((~summary.on_time) & (summary.expiry_time_ms <= duration * 1000)).sum()
        ),
        deadline_pending_at_stop=int(
            ((~summary.on_time) & (summary.expiry_time_ms > duration * 1000)).sum()
        ),
        undelivered=n - len(delivered),
        pdr_pct=ratio(len(delivered)),
        dsdr_pct=ratio(len(ontime)),
        loss_pct=ratio(n - len(delivered)),
        mean_delay_ms=avg(delay),
        median_delay_ms=float(delay.median()) if len(delay) else None,
        p95_delay_ms=float(delay.quantile(0.95)) if len(delay) else None,
        mean_hops=avg(delivered.hop_count),
        throughput_kbps=float(delivered.payload_bytes.sum() * 8 / duration / 1000),
        data_transmissions=len(tx),
        forwarding_transmissions=len(forwarded),
        forwarding_attempts=int((events.event_type == "FORWARD_EXECUTED").sum()),
        duplicate_transmissions=duplicates,
        control_transmissions=int((events.event_type == "CONTROL_TX").sum()),
        udp_protocol_bytes=int(
            (tx.payload_bytes + 76).sum()
            + 76 * (events.event_type == "CONTROL_TX").sum()
        ),
        forwarding_per_delivered=float(len(forwarded) / len(delivered))
        if len(delivered)
        else None,
        unique_expired=int(expiry.packet_id.nunique()),
        expiration_events=len(expiry),
        duplicate_suppressions=int((events.event_type == "DUPLICATE_SUPPRESSED").sum()),
        queue_drops=int((events.drop_reason == "QUEUE_OVERFLOW").sum()),
        infeasible_events=int(
            (
                (events.drop_reason == "DEADLINE_INFEASIBLE")
                & (events.event_type == "CANDIDATE_EVALUATED")
            ).sum()
        ),
        mean_forward_wait_ms=avg(
            events.loc[events.event_type == "FORWARD_SCHEDULED", "forwarding_wait_ms"]
        ),
    )
    result["per_class"] = []
    result["per_flow"] = []
    for columns, key in [
        (["traffic_class"], "per_class"),
        (["source_id", "destination_id"], "per_flow"),
    ]:
        for group, frame in summary.groupby(columns):
            values = group if isinstance(group, tuple) else (group,)
            result[key].append(
                {
                    **dict(zip(columns, map(int, values))),
                    "generated": len(frame),
                    "delivered": int(frame.delivered.sum()),
                    "on_time": int(frame.on_time.sum()),
                    "dsdr_pct": float(100 * frame.on_time.mean()),
                    "pdr_pct": float(100 * frame.delivered.mean()),
                }
            )
    assert (
        result["on_time_delivered"] <= result["unique_delivered"] <= result["generated"]
    )
    return result


def process_run(path, config):
    path = Path(path)
    events = read_events(path / "packet_events.csv")
    summary = summarize(events)
    summary.to_csv(path / "packet_summary.csv", index=False)
    result = metrics(summary, events, config["duration"])
    radio = pd.read_csv(path / "radio_events.csv")
    result["phy_transmissions"] = int((radio.event_type == "PHY_TX_BEGIN").sum())
    result["phy_rx_drop_events"] = int((radio.event_type == "PHY_RX_DROP").sum())
    (path / "metrics.json").write_text(json.dumps(result, indent=2, allow_nan=False))
    pd.DataFrame([{k: v for k, v in result.items() if not isinstance(v, list)}]).to_csv(
        path / "metrics.csv", index=False
    )
    return result
