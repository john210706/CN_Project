import subprocess
import pandas as pd
import pytest
from scripts.configuration import load_config
from scripts.run_simulation import run, executable
from analysis.metrics import read_events

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def outputs(tmp_path_factory):
    root = tmp_path_factory.mktemp("ns3")
    results = {}
    for protocol in ["fixed", "opportunistic", "deadline_aware"]:
        c = load_config(
            "config/diamond.yaml",
            {
                "protocol": protocol,
                "start": 0.8,
                "stop": 1.4,
                "duration": 1.8,
                "rate": 10,
            },
        )
        p, m = run(c, root)
        results[protocol] = (p, m, read_events(p / "packet_events.csv"), c)
    return results


def test_cpp():
    result = subprocess.run(
        [str(executable()), "--selfTest=1"], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert "self-tests passed" in result.stdout


@pytest.mark.parametrize("protocol", ["fixed", "opportunistic", "deadline_aware"])
def test_wireless_multihop(outputs, protocol):
    p, m, e, c = outputs[protocol]
    assert m["generated"] > 0 and m["unique_delivered"] > 0
    assert m["mean_hops"] >= 2 and m["phy_transmissions"] > m["data_transmissions"]
    receptions = e[e.event_type == "PACKET_RX"]
    assert receptions.groupby("packet_id").current_node_id.nunique().max() >= 3
    if protocol == "fixed":
        assert set(
            e[(e.event_type == "PACKET_TX") & (e.current_node_id != 0)].current_node_id
        ) == {1}
    if protocol == "deadline_aware":
        assert (e[e.event_type == "PACKET_TX"].remaining_time_ms > 0).all()
        assert m["infeasible_events"] > 0
    else:
        assert m["infeasible_events"] == 0


def test_suppression(outputs):
    assert outputs["opportunistic"][1]["duplicate_suppressions"] > 0
    e = outputs["opportunistic"][2]
    cancelled = e[e.event_type == "DUPLICATE_SUPPRESSED"]
    for row in cancelled.itertuples():
        received = e[
            (e.packet_id == row.packet_id)
            & (e.current_node_id == row.current_node_id)
            & (e.event_type == "PACKET_RX")
        ]
        assert any(abs(received.simulation_time_ms - row.simulation_time_ms) < 1e-8)


def test_reproducibility(outputs, tmp_path):
    old, metrics, e, c = outputs["deadline_aware"]
    new, new_metrics = run(c, tmp_path)
    assert metrics == new_metrics
    assert (old / "packet_events.csv").read_bytes() == (
        new / "packet_events.csv"
    ).read_bytes()
    assert (old / "node_positions.csv").read_bytes() == (
        new / "node_positions.csv"
    ).read_bytes()


def test_expiry(tmp_path):
    c = load_config(
        "config/diamond.yaml",
        {"deadline": 0.2, "processing": 5, "start": 0.8, "stop": 1.0, "duration": 1.3},
    )
    p, m = run(c, tmp_path)
    e = read_events(p / "packet_events.csv")
    assert m["expiration_events"] == m["generated"] and m["data_transmissions"] == 0
    assert "EXPIRED_BEFORE_FORWARD" in set(e.drop_reason)


def test_line_mobility_channel_congestion(tmp_path):
    base = {
        "topology": "line",
        "nodes": 5,
        "start": 0.8,
        "stop": 1.4,
        "duration": 1.8,
        "spacing": 80,
        "protocol": "opportunistic",
    }
    p, normal = run(load_config(overrides=base), tmp_path)
    assert normal["unique_delivered"] > 0 and normal["mean_hops"] >= 4
    _, bad = run(load_config(overrides={**base, "pathLoss": 5}), tmp_path)
    assert bad["unique_delivered"] < normal["unique_delivered"]
    p, moving = run(
        load_config(overrides={**base, "mobility": "velocity", "speed": 50}), tmp_path
    )
    positions = pd.read_csv(p / "node_positions.csv")
    assert positions[positions.node_id == 1].x.nunique() > 1
    assert moving["unique_delivered"] < normal["unique_delivered"]
    _, busy = run(
        load_config(
            overrides={**base, "rate": 500, "processing": 5, "queueCapacity": 2}
        ),
        tmp_path,
    )
    assert busy["queue_drops"] > 0 and busy["generated"] > normal["generated"]


def test_cli(tmp_path):
    r = subprocess.run(
        [".venv/bin/python", "scripts/run_simulation.py", "--nodes", "-1"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 2 and "nodes" in r.stderr.lower()
    r = subprocess.run(
        [str(executable()), "--PrintHelp"], capture_output=True, text=True
    )
    assert r.returncode == 0 and "--protocol" in r.stdout and "--weights" in r.stdout


def test_deadline_changes_actual_relay_and_uses_observed_link(tmp_path):
    seen = {}
    for proto in ["opportunistic", "deadline_aware"]:
        p, m = run(
            load_config("config/deadline-decision.yaml", {"protocol": proto}), tmp_path
        )
        e = read_events(p / "packet_events.csv")
        seen[proto] = e
    basic = seen["opportunistic"]
    aware = seen["deadline_aware"]
    assert set(
        basic[
            (basic.packet_id == 7) & (basic.event_type == "PACKET_TX")
        ].current_node_id
    ) == {0, 1}
    assert set(
        aware[
            (aware.packet_id == 7) & (aware.event_type == "PACKET_TX")
        ].current_node_id
    ) == {0, 2}
    decisions = aware[
        (aware.packet_id == 7)
        & (aware.event_type == "CANDIDATE_EVALUATED")
        & (aware.hop_count == 1)
    ].set_index("current_node_id")
    assert decisions.loc[1, "link_quality"] > decisions.loc[2, "link_quality"]
    assert decisions.loc[1, "drop_reason"] == "DEADLINE_INFEASIBLE"
    assert decisions.loc[2, "drop_reason"] == ""


def test_hidden_candidates_retain_duplicates(tmp_path):
    outcomes = []
    for height in [20, 80]:
        _, m = run(
            load_config(
                "config/diamond.yaml",
                {
                    "protocol": "opportunistic",
                    "slowProcessing": 15,
                    "power": 30,
                    "diamondHeight": height,
                    "rate": 5,
                },
            ),
            tmp_path,
        )
        outcomes.append(m)
    assert outcomes[0]["duplicate_suppressions"] > 0
    assert (
        outcomes[1]["duplicate_transmissions"] > outcomes[0]["duplicate_transmissions"]
    )


def test_poisson_multiflow_and_waypoint(tmp_path):
    c = load_config(
        overrides={
            "topology": "grid",
            "nodes": 10,
            "traffic": "poisson",
            "pairs": [[0, 9], [1, 8]],
            "mobility": "waypoint",
            "speed": 5,
            "area": 250,
            "duration": 2.0,
            "start": 0.8,
            "stop": 1.3,
        }
    )
    p, m = run(c, tmp_path)
    e = read_events(p / "packet_events.csv")
    created = e[e.event_type == "PACKET_CREATED"]
    assert not created.packet_id.duplicated().any() and set(created.source_id) == {0, 1}
    assert len(m["per_flow"]) == 2
    positions = pd.read_csv(p / "node_positions.csv")
    assert positions[positions.node_id == 1].x.nunique() > 1
