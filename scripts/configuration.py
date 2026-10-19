from pathlib import Path
import math
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "config/default.yaml"


def load_config(path=None, overrides=None):
    config = yaml.safe_load(DEFAULT.read_text())
    if path:
        supplied = yaml.safe_load(Path(path).read_text())
        if not isinstance(supplied, dict):
            raise ValueError("Configuration must be a YAML mapping")
        config.update(supplied)
    config.update(overrides or {})
    validate(config)
    return config


def validate(c):
    expected = set(yaml.safe_load(DEFAULT.read_text()))
    if set(c) - expected:
        raise ValueError(f"Unknown settings: {sorted(set(c) - expected)}")
    enums = {
        "protocol": ["fixed", "opportunistic", "deadline_aware"],
        "topology": ["diamond", "line", "grid", "random", "mobile"],
        "mobility": ["static", "waypoint", "velocity"],
        "traffic": ["constant", "poisson"],
        "rateMode": [f"OfdmRate{x}Mbps" for x in (6, 9, 12, 18, 24, 36, 48, 54)],
    }
    for key, options in enums.items():
        if c[key] not in options:
            raise ValueError(f"{key} must be one of {options}")
    for key in expected - set(enums) - {"weights", "mix", "deadlines", "pairs"}:
        if (
            isinstance(c[key], bool)
            or not isinstance(c[key], (int, float))
            or not math.isfinite(c[key])
        ):
            raise ValueError(f"{key} must be finite numeric")
    for key in [
        "nodes",
        "seed",
        "run",
        "payload",
        "flows",
        "queueCapacity",
        "maxHops",
        "lossNode",
    ]:
        if not isinstance(c[key], int):
            raise ValueError(f"{key} must be an integer")
    if not 2 <= c["nodes"] <= 500 or (c["topology"] == "diamond" and c["nodes"] != 4):
        raise ValueError("Use 2–500 nodes; diamond requires exactly four")
    if not 1 <= c["payload"] <= 1400 or not 1 <= c["flows"] < c["nodes"]:
        raise ValueError("Invalid payload size or flow count")
    if not 0 <= c["start"] < c["stop"] < c["duration"]:
        raise ValueError("Require 0 <= start < stop < duration")
    for key in [
        "rate",
        "spacing",
        "area",
        "range",
        "pathLoss",
        "perHop",
        "hello",
        "queueCapacity",
        "seed",
        "run",
        "maxHops",
    ]:
        if c[key] <= 0:
            raise ValueError(f"{key} must be positive")
    if (
        c["maxHops"] > 65535
        or c["rate"] > 100000
        or c["seed"] > 4294967295
        or c["run"] > 4294967295
    ):
        raise ValueError("Hop count, rate, seed or run exceeds supported bound")
    for key in [
        "speed",
        "pause",
        "processing",
        "slowProcessing",
        "minHoldoff",
        "maxHoldoff",
        "safety",
        "deadline",
        "diamondHeight",
    ]:
        if c[key] < 0:
            raise ValueError(f"{key} cannot be negative")
    if (
        c["maxHoldoff"] < c["minHoldoff"]
        or not 0 <= c["loss"] <= 1
        or not 0 <= c["lossNode"] <= 4294967295
    ):
        raise ValueError("Invalid holdoff or injected loss")
    for key in ["weights", "mix", "deadlines"]:
        a = c[key]
        if (
            not isinstance(a, list)
            or len(a) != 4
            or any(
                isinstance(x, bool)
                or not isinstance(x, (float, int))
                or not math.isfinite(x)
                or x < 0
                for x in a
            )
        ):
            raise ValueError(f"{key} requires four finite nonnegative numbers")
        if key != "deadlines" and not math.isclose(sum(a), 1.0, abs_tol=1e-6):
            raise ValueError(f"{key} must sum to one")
        if key == "deadlines" and min(a) <= 0:
            raise ValueError("Deadlines must be positive")
    if not isinstance(c["pairs"], list):
        raise ValueError("pairs must be a list of [source, destination]")
    for p in c["pairs"]:
        if (
            not isinstance(p, list)
            or len(p) != 2
            or any(
                not isinstance(x, int) or isinstance(x, bool) or not 0 <= x < c["nodes"]
                for x in p
            )
            or p[0] == p[1]
        ):
            raise ValueError("Invalid source-destination pair")
    if c["mobility"] == "waypoint" and c["speed"] <= 0:
        raise ValueError(
            "Waypoint speed must be positive; choose static for zero speed"
        )
    return c


def arguments(c):
    args = []
    for key, value in c.items():
        if key == "pairs":
            if not value:
                continue
            value = ",".join(f"{s}:{d}" for s, d in value)
        elif isinstance(value, list):
            value = ",".join(map(str, value))
        args.append(f"--{key}={value}")
    return args
