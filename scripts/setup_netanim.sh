#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh

[[ "$(uname -sm)" == "Linux x86_64" ]] || { echo "This setup script supports Linux x86_64" >&2; exit 1; }
[[ -x .tools/bin/micromamba ]] || { echo "Run bash scripts/setup.sh first" >&2; exit 1; }

.tools/bin/micromamba install -y -p "$PWD/.tools/env" -c conda-forge qt6-main
[[ -d vendor/netanim-3.110 ]] || git clone --depth 1 --branch netanim-3.110 https://gitlab.com/nsnam/netanim.git vendor/netanim-3.110
python scripts/customize_netanim.py
cmake -S vendor/netanim-3.110 -B .tools/netanim-build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PWD/.tools/netanim"
cmake --build .tools/netanim-build -j "${BUILD_JOBS:-2}"
cmake --install .tools/netanim-build
echo "NetAnim installed at $PWD/.tools/netanim/bin/netanim"
