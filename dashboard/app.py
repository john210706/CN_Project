from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scripts.configuration import ROOT, load_config
from scripts.run_simulation import run, executable
from analysis.load_results import discover, load_run
from analysis.aggregate import aggregate

st.set_page_config(
    page_title="Deadline-Aware Opportunistic Routing Lab", page_icon="📡", layout="wide"
)
st.title("Deadline-Aware Opportunistic Routing Lab")
st.caption("Real NS-3.45 Wi-Fi • application-layer forwarding • measured packet traces")
with st.sidebar:
    st.header("Run a simulation")
    protocol = st.selectbox(
        "Protocol", ["fixed", "opportunistic", "deadline_aware"], index=2
    )
    topology = st.selectbox("Topology", ["diamond", "line", "grid", "random", "mobile"])
    nodes = st.number_input("Nodes", 2, 100, 4 if topology == "diamond" else 10)
    rate = st.number_input("Packets/s per flow", 1.0, 2000.0, 20.0)
    deadline = st.number_input("Deadline (ms; 0 = class defaults)", 0.0, 2000.0, 50.0)
    mobility = st.selectbox("Mobility", ["static", "waypoint", "velocity"])
    seed = st.number_input("Seed", 1, 100000, 1)
    channel = st.selectbox("Path-loss exponent", [2.6, 3.0, 3.8], index=1)
    try:
        executable()
        available = True
    except FileNotFoundError:
        available = False
        st.info("Install/build NS-3 to launch runs. Existing results remain available.")
    if st.button("Run NS-3", type="primary", disabled=not available):
        try:
            config = load_config(
                overrides=dict(
                    protocol=protocol,
                    topology=topology,
                    nodes=nodes,
                    rate=rate,
                    deadline=deadline,
                    mobility=mobility,
                    seed=seed,
                    pathLoss=channel,
                )
            )
            with st.spinner("Executing Wi-Fi simulation…"):
                path, _ = run(config)
            st.session_state["selected_run"] = str(path)
            st.success("Simulation completed")
        except Exception as e:
            st.error(str(e))
    st.divider()
    root = st.text_input("Results directory", str(ROOT / "results/raw"))
runs, errors = discover(root)
if errors:
    with st.expander(f"{len(errors)} unavailable or failed runs"):
        st.write(errors)
if runs.empty:
    st.info(
        "No successful simulations here yet. Run NS-3 from the sidebar or use make demo."
    )
    st.stop()
options = runs.path.tolist()
selected = st.selectbox(
    "Recorded run",
    options,
    index=options.index(st.session_state["selected_run"])
    if st.session_state.get("selected_run") in options
    else len(options) - 1,
    format_func=lambda p: Path(p).name,
)
try:
    meta, events, positions, summary, metrics = load_run(selected)
except (ValueError, OSError, KeyError, pd.errors.ParserError) as e:
    st.error(f"Cannot load result: {e}")
    st.stop()
config = meta["config"]
st.caption(
    f"{config['protocol']} · {config['topology']} · {config['nodes']} nodes · seed {config['seed']} · run {config['run']}"
)
cols = st.columns(6)
for col, key, label in zip(
    cols,
    [
        "generated",
        "unique_delivered",
        "on_time_delivered",
        "pdr_pct",
        "dsdr_pct",
        "mean_delay_ms",
    ],
    ["Generated", "Delivered", "On time", "PDR (%)", "DSDR (%)", "Mean delay (ms)"],
):
    value = metrics.get(key)
    col.metric(
        label,
        "—" if value is None else f"{value:.2f}" if isinstance(value, float) else value,
    )
overview, playback, candidates, comparison, experiments, method = st.tabs(
    [
        "Overview",
        "Packet playback",
        "Candidate decisions",
        "Compare protocols",
        "Experiments & exports",
        "Methodology",
    ]
)
with overview:
    a, b = st.columns(2)
    with a:
        counts = pd.DataFrame(
            {
                "Outcome": ["On time", "Late", "Undelivered"],
                "Packets": [
                    metrics["on_time_delivered"],
                    metrics["late_delivered"],
                    metrics["undelivered"],
                ],
            }
        )
        st.plotly_chart(
            px.bar(
                counts,
                x="Outcome",
                y="Packets",
                color="Outcome",
                title="Unique packet outcomes",
            ),
            use_container_width=True,
        )
    with b:
        st.dataframe(
            pd.DataFrame(
                {
                    "Metric": [
                        "Forwarding transmissions",
                        "Extra same-hop transmissions",
                        "Suppressed timers",
                        "Unique expiration packets",
                        "Queue drop events",
                        "PHY transmissions",
                        "PHY reception drop events",
                    ],
                    "Observed": [
                        metrics[k]
                        for k in [
                            "forwarding_transmissions",
                            "duplicate_transmissions",
                            "duplicate_suppressions",
                            "unique_expired",
                            "queue_drops",
                            "phy_transmissions",
                            "phy_rx_drop_events",
                        ]
                    ],
                }
            ),
            hide_index=True,
            use_container_width=True,
        )
        st.caption(
            "Expiration events at one branch can coexist with delivery through another branch."
        )
    st.dataframe(pd.DataFrame(metrics["per_class"]), hide_index=True)
    st.dataframe(pd.DataFrame(metrics["per_flow"]), hide_index=True)
with playback:
    ids = summary.packet_id.astype(str).tolist()
    if not ids:
        st.info("No generated packets in this run.")
    else:
        packet_id = st.selectbox("Packet identity (source << 32 | sequence)", ids)
        trace = events[
            (events.packet_id.astype(str) == packet_id)
            & ~events.event_type.str.startswith("CONTROL")
        ].reset_index(drop=True)
        speed = st.select_slider(
            "Playback speed", options=[0.25, 0.5, 1.0, 2.0, 4.0], value=1.0
        )
        index = (
            st.slider("Step through recorded events", 0, max(0, len(trace) - 1), 0)
            if len(trace) > 1
            else 0
        )

        def drawing(i):
            event = trace.iloc[i]
            time = event.simulation_time_ms
            snapshot = (
                positions[positions.simulation_time_ms <= time]
                .sort_values("simulation_time_ms")
                .groupby("node_id")
                .tail(1)
            )
            source = int(trace.iloc[0].source_id)
            dest = int(trace.iloc[0].destination_id)
            roles = [
                "Source" if n == source else "Destination" if n == dest else "Relay"
                for n in snapshot.node_id
            ]
            colors = [
                "#3b82f6"
                if r == "Source"
                else "#00c9a7"
                if r == "Destination"
                else "#e5a028"
                for r in roles
            ]
            edges = trace.iloc[: i + 1]
            edges = edges[edges.event_type == "PACKET_RX"]
            xs = []
            ys = []
            # Reception edges use the latest sampled positions at that reception, never inferred connectivity.
            for row in edges.itertuples():
                pos = (
                    positions[positions.simulation_time_ms <= row.simulation_time_ms]
                    .groupby("node_id")
                    .tail(1)
                    .set_index("node_id")
                )
                if (
                    row.previous_forwarder_id in pos.index
                    and row.current_node_id in pos.index
                ):
                    a = pos.loc[row.previous_forwarder_id]
                    b = pos.loc[row.current_node_id]
                    xs.extend([a.x, b.x, None])
                    ys.extend([a.y, b.y, None])
            return [
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    line=dict(color="#718096", width=2),
                    name="Observed receptions",
                ),
                go.Scatter(
                    x=snapshot.x,
                    y=snapshot.y,
                    mode="markers+text",
                    text=snapshot.node_id,
                    textposition="top center",
                    marker=dict(size=20, color=colors),
                    customdata=roles,
                    hovertemplate="Node %{text}: %{customdata}<extra></extra>",
                    name="Nodes",
                ),
            ]

        frames = [
            go.Frame(
                data=drawing(i),
                name=str(i),
                layout=go.Layout(
                    title=f"{trace.iloc[i].simulation_time_ms:.3f} ms · {trace.iloc[i].event_type}"
                ),
            )
            for i in range(len(trace))
        ]
        fig = go.Figure(data=drawing(index), frames=frames)
        fig.update_layout(
            height=460,
            title=f"{trace.iloc[index].simulation_time_ms:.3f} ms · {trace.iloc[index].event_type}",
            xaxis=dict(
                title="x (m)", range=[positions.x.min() - 20, positions.x.max() + 20]
            ),
            yaxis=dict(
                title="y (m)",
                scaleanchor="x",
                range=[positions.y.min() - 20, positions.y.max() + 20],
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    bgcolor="#e6edf5",
                    font=dict(color="#101827"),
                    buttons=[
                        dict(
                            label="▶ Play",
                            method="animate",
                            args=[
                                None,
                                {
                                    "frame": {
                                        "duration": int(600 / speed),
                                        "redraw": True,
                                    },
                                    "transition": {"duration": 0},
                                    "fromcurrent": True,
                                },
                            ],
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[
                                [None],
                                {"mode": "immediate", "frame": {"duration": 0}},
                            ],
                        ),
                    ],
                )
            ],
            sliders=[
                dict(
                    steps=[
                        dict(
                            method="animate",
                            args=[
                                [str(i)],
                                {
                                    "mode": "immediate",
                                    "frame": {"duration": 0, "redraw": True},
                                    "transition": {"duration": 0},
                                },
                            ],
                            label=str(i),
                        )
                        for i in range(len(trace))
                    ]
                )
            ],
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Playback advances through recorded events. Positions use the preceding 100 ms sample; lines show actual receptions, not a connectivity prediction. Playback speed is a visual aid."
        )
        st.dataframe(trace, use_container_width=True, hide_index=True)
with candidates:
    decisions = events[events.event_type == "CANDIDATE_EVALUATED"]
    if decisions.empty:
        st.info("No receiver candidate decisions in this run.")
    else:
        chosen = st.selectbox("Inspect packet", decisions.packet_id.unique())
        data = decisions[decisions.packet_id == chosen]
        st.dataframe(
            data[
                [
                    "simulation_time_ms",
                    "current_node_id",
                    "previous_forwarder_id",
                    "remaining_time_ms",
                    "estimated_remaining_delay_ms",
                    "link_quality",
                    "normalized_progress",
                    "queue_delay_ms",
                    "slack_ms",
                    "candidate_score",
                    "forwarding_wait_ms",
                    "drop_reason",
                ]
            ],
            hide_index=True,
            use_container_width=True,
        )
        st.plotly_chart(
            px.scatter(
                data,
                x="remaining_time_ms",
                y="estimated_remaining_delay_ms",
                color="current_node_id",
                size="candidate_score",
                hover_data=["drop_reason", "forwarding_wait_ms"],
                title="Remaining lifetime versus predicted delivery delay",
            ),
            use_container_width=True,
        )
        st.dataframe(
            events[
                (events.packet_id == chosen)
                & events.event_type.isin(
                    [
                        "FORWARD_EXECUTED",
                        "FORWARD_CANCELLED",
                        "PACKET_EXPIRED",
                        "DESTINATION_DELIVERED",
                    ]
                )
            ],
            hide_index=True,
        )
with comparison:
    batch = st.selectbox("Comparable experiment batch", runs.batch.unique())
    filtered = runs[runs.batch == batch]
    scenario = st.selectbox("Scenario", filtered.scenario.unique())
    filtered = filtered[filtered.scenario == scenario]
    if batch == "standalone":
        st.info(
            "Standalone runs may differ in configuration. Use an experiment batch for controlled comparisons."
        )
    node_filter = st.multiselect(
        "Node counts",
        sorted(filtered.nodes.unique()),
        default=sorted(filtered.nodes.unique()),
    )
    seed_filter = st.multiselect(
        "Seeds", sorted(filtered.seed.unique()), default=sorted(filtered.seed.unique())
    )
    load_filter = st.multiselect(
        "Offered loads (packets/s/flow)",
        sorted(filtered.rate.unique()),
        default=sorted(filtered.rate.unique()),
    )
    deadline_filter = st.multiselect(
        "Deadline override (ms; 0 = mixed)",
        sorted(filtered.deadline.unique()),
        default=sorted(filtered.deadline.unique()),
    )
    filtered = filtered[
        filtered.nodes.isin(node_filter)
        & filtered.seed.isin(seed_filter)
        & filtered.rate.isin(load_filter)
        & filtered.deadline.isin(deadline_filter)
    ]
    traffic_class = st.selectbox("Traffic class", ["All", 0, 1, 2, 3])
    if traffic_class != "All":
        filtered = filtered.copy()
        for idx, row in filtered.iterrows():
            m = json.loads((Path(row.path) / "metrics.json").read_text())
            classes = {r["traffic_class"]: r for r in m["per_class"]}
            for key in ["pdr_pct", "dsdr_pct"]:
                filtered.loc[idx, key] = classes.get(traffic_class, {}).get(
                    key, float("nan")
                )
        st.caption(
            "Class filter applies to PDR and DSDR. Other metrics describe the whole run."
        )
    metric = st.selectbox(
        "Comparison metric",
        [
            "dsdr_pct",
            "pdr_pct",
            "mean_delay_ms",
            "throughput_kbps",
            "forwarding_transmissions",
            "duplicate_transmissions",
            "unique_expired",
        ],
    )
    if not filtered.empty:
        st.plotly_chart(
            px.box(
                filtered,
                x="protocol",
                y=metric,
                color="protocol",
                points="all",
                color_discrete_map={
                    "fixed": "#3b82f6",
                    "opportunistic": "#e5a028",
                    "deadline_aware": "#00b89c",
                },
            ),
            use_container_width=True,
        )
        st.dataframe(aggregate(filtered), hide_index=True)
        st.caption(
            "95% Student-t intervals across independent seeds; one seed has no interval. Delay excludes undelivered packets."
        )
with experiments:
    st.dataframe(runs, use_container_width=True, hide_index=True)
    for file in [
        "packet_summary.csv",
        "packet_events.csv",
        "metrics.json",
        "run_metadata.json",
    ]:
        st.download_button(
            f"Download {file}", (Path(selected) / file).read_bytes(), file_name=file
        )
    report = ROOT / "docs/final-report.md"
    if report.exists():
        st.download_button(
            "Download academic report", report.read_text(), file_name="final-report.md"
        )
with method:
    st.markdown(
        (ROOT / "docs/dashboard-methodology.md").read_text()
        if (ROOT / "docs/dashboard-methodology.md").exists()
        else "See docs/methodology.md for the experimental assumptions."
    )
