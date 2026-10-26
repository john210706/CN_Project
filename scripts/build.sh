#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
for tool in python3 cmake ninja; do command -v "$tool" >/dev/null || { echo "Missing $tool; run setup.sh" >&2; exit 1; }; done
[[ -f "$NS3_DIR/ns3" ]] || { echo "NS3_DIR must point to NS-3.45 source" >&2; exit 1; }
[[ "$(cat "$NS3_DIR/VERSION")" == "3.45" ]] || { echo "This project is verified against NS-3.45 only" >&2; exit 1; }
target="$NS3_DIR/scratch/deadline-routing"
if [[ -e "$target" && "$(readlink -f "$target")" != "$PROJECT_ROOT/simulation" ]]; then
  echo "Refusing to replace existing $target" >&2; exit 1
fi
ln -sfn "$PROJECT_ROOT/simulation" "$target"
cd "$NS3_DIR"
python3 ns3 configure --build-profile=release --enable-modules=core,network,internet,wifi,mobility,netanim --disable-examples --disable-tests -- -G Ninja
python3 ns3 build deadline-routing -j "${BUILD_JOBS:-2}"
