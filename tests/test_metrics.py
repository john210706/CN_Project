import pandas as pd
import pytest
from analysis.metrics import metrics, summarize, read_events
from analysis.aggregate import aggregate, comparisons
from analysis.load_results import discover


def fixture_events():
    events = []
    for i in range(100):
        row = dict(
            simulation_time_ms=0,
            packet_id=i,
            source_id=0,
            destination_id=1,
            current_node_id=0,
            traffic_class=0,
            creation_time_ms=0,
            expiry_time_ms=50,
            payload_bytes=100,
            hop_count=0,
            drop_reason="",
            forwarding_wait_ms=0,
        )
        events.append(dict(row, event_type="PACKET_CREATED"))
        if i < 75:
            events.append(
                dict(
                    row,
                    event_type="DESTINATION_DELIVERED",
                    current_node_id=1,
                    simulation_time_ms=50 if i < 60 else 51,
                    hop_count=2,
                )
            )
    return pd.DataFrame(events)


def test_known_counts_boundary_and_duplicates():
    e = fixture_events()
    e = pd.concat(
        [e, e[e.event_type == "DESTINATION_DELIVERED"].iloc[:1]], ignore_index=True
    )
    s = summarize(e)
    m = metrics(s, e, 1)
    assert m["pdr_pct"] == 75 and m["dsdr_pct"] == 60 and m["late_delivered"] == 15
    assert m["throughput_kbps"] == 60
    assert m["unique_delivered"] == 75


def test_zero_and_invalid():
    e = fixture_events().iloc[:0]
    m = metrics(summarize(e), e, 1)
    assert m["pdr_pct"] == 0 and m["mean_delay_ms"] is None
    e = fixture_events()
    e.loc[e.event_type == "DESTINATION_DELIVERED", "current_node_id"] = 2
    with pytest.raises(ValueError):
        summarize(e)


def test_missing_and_malformed(tmp_path):
    runs, errors = discover(tmp_path)
    assert runs.empty and not errors
    (tmp_path / "run_metadata.json").write_text("broken")
    runs, errors = discover(tmp_path)
    assert runs.empty and errors
    bad = tmp_path / "bad.csv"
    bad.write_text("not,valid\n1,2\n")
    with pytest.raises(ValueError):
        read_events(bad)


def test_statistics():
    from analysis.aggregate import METRICS

    rows = [
        dict(batch="b", scenario="s", protocol=p, **{k: v for k in METRICS})
        for p in ["fixed", "deadline_aware"]
        for v in [40.0, 60.0]
    ]
    stats = aggregate(pd.DataFrame(rows))
    assert (stats.dsdr_pct_mean == 50).all()
    assert (stats.dsdr_pct_n == 2).all() and (stats.dsdr_pct_ci95 > 0).all()
    assert comparisons(stats).iloc[0].dsdr_difference_pp == 0


def test_deadline_not_yet_elapsed_is_not_confirmed_miss():
    e = fixture_events()
    s = summarize(e)
    e = e[e.event_type == "PACKET_CREATED"]
    s = summarize(e)
    m = metrics(s, e, 0.01)
    assert m["deadline_missed"] == 0
    assert m["deadline_pending_at_stop"] == 100


def test_metadata_wrong_json_type(tmp_path):
    (tmp_path / "run_metadata.json").write_text("[]")
    runs, errors = discover(tmp_path)
    assert runs.empty and len(errors) == 1
