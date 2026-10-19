import pytest
from scripts.configuration import load_config, arguments
from scripts.run_experiments import plan
from pathlib import Path


@pytest.mark.parametrize(
    "override",
    [
        {"nodes": 1},
        {"topology": "diamond", "nodes": 5},
        {"rate": -1},
        {"deadline": -3},
        {"protocol": "fake"},
        {"weights": [1, 1, 1, 1]},
        {"weights": [float("nan"), 0, 0, 1]},
        {"mix": [1, 0, 0]},
        {"start": 5},
        {"pairs": [[0, 0]]},
        {"surprise": 1},
        {"nodes": 4.5},
        {"payload": 9000},
        {"mobility": "waypoint", "speed": 0},
    ],
)
def test_invalid(override):
    with pytest.raises(ValueError):
        load_config(overrides=override)


def test_configs():
    for path in Path("config").glob("*.yaml"):
        if "matrix" not in path.name:
            load_config(path)
    assert "--protocol=deadline_aware" in arguments(load_config())
    assert len(plan("config/experiment-matrix.yaml")) == 255
