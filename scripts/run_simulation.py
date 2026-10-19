#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import hashlib
import os
from pathlib import Path
import platform
import subprocess
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.configuration import ROOT, load_config, validate, arguments
from analysis.metrics import process_run


def executable():
    ns3 = Path(os.environ.get("NS3_DIR", ROOT / "vendor/ns-3.45")).resolve()
    files = list(
        (ns3 / "build/scratch/deadline-routing").glob("ns3.45-deadline-routing*")
    )
    files = [f for f in files if f.is_file() and os.access(f, os.X_OK)]
    if len(files) != 1:
        raise FileNotFoundError(
            "NS-3.45 executable unavailable; run bash scripts/build.sh or set NS3_DIR"
        )
    return files[0]


def run(config, output_root=None):
    validate(config)
    binary = executable()
    root = Path(output_root or ROOT / "results/raw")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    path = root / f"{stamp}_{config['protocol']}_{uuid.uuid4().hex[:8]}"
    path.mkdir(parents=True, exist_ok=False)
    trace_dir = path / "trace"
    command = [str(binary), *arguments(config), f"--output={trace_dir}"]
    git = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
    )
    metadata = {
        "schema_version": 1,
        "ns3_version": "3.45",
        "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "config": config,
        "command": command,
        "timestamp_utc": stamp,
        "git_commit": git.stdout.strip() if git.returncode == 0 else None,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "status": "running",
    }
    meta_path = path / "run_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2))
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=max(120, config["duration"] * 60),
        )
        (path / "stdout.log").write_text(completed.stdout)
        (path / "stderr.log").write_text(completed.stderr)
        if completed.returncode:
            raise RuntimeError(
                f"Simulator exited {completed.returncode}: {completed.stderr[-3000:]}"
            )
        for file in trace_dir.iterdir():
            file.rename(path / file.name)
        trace_dir.rmdir()
        result = process_run(path, config)
        metadata["status"] = "success"
    except Exception as error:
        metadata.update(status="failed", error=str(error))
        raise
    finally:
        meta_path.write_text(json.dumps(metadata, indent=2))
    return path, result


def main():
    parser = argparse.ArgumentParser(description="Run genuine NS-3 Wi-Fi forwarding")
    parser.add_argument("--config", type=Path)
    for key, typ in [
        ("protocol", str),
        ("nodes", int),
        ("topology", str),
        ("seed", int),
        ("rate", float),
        ("deadline", float),
        ("mobility", str),
        ("duration", float),
        ("run", int),
    ]:
        parser.add_argument("--" + key, type=typ)
    parser.add_argument("--output-root", type=Path)
    args = vars(parser.parse_args())
    cfg = args.pop("config")
    root = args.pop("output_root")
    try:
        c = load_config(cfg, {k: v for k, v in args.items() if v is not None})
        path, m = run(c, root)
        print(
            f"{path}\nPDR={m['pdr_pct']:.2f}% DSDR={m['dsdr_pct']:.2f}% delivered={m['unique_delivered']}/{m['generated']}"
        )
    except (
        ValueError,
        FileNotFoundError,
        RuntimeError,
        subprocess.TimeoutExpired,
    ) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
