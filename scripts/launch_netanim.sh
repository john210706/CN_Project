#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

viewer="$PWD/.tools/netanim/bin/netanim"
[[ -x "$viewer" ]] || { echo "NetAnim viewer is not built; run bash scripts/setup_netanim.sh" >&2; exit 1; }

xml="${1:-}"
if [[ -z "$xml" ]]; then
  xml="$(find results/raw -name animation.xml -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)"
fi
[[ -n "$xml" && -f "$xml" ]] || { echo "No animation.xml found; run a simulation first" >&2; exit 1; }

xml="$(realpath "$xml")"
echo "NetAnim is opening in $(dirname "$xml")"
echo "Loading $(basename "$xml") and starting playback automatically."
cd "$(dirname "$xml")"
exec "$viewer" "$xml"
