#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh
if ! command -v cmake >/dev/null || ! command -v ninja >/dev/null || ! command -v make >/dev/null || ! command -v "${CXX:-g++}" >/dev/null || ! python3 -c 'import sys; raise SystemExit(not (3,10) <= sys.version_info[:2] < (3,14))'; then
  echo 'Installing project-local Linux x86_64 compiler and Python environment.'
  [[ "$(uname -sm)" == 'Linux x86_64' ]] || { echo 'Install a C++ compiler, Python, CMake and Ninja for your platform.'; exit 1; }
  mkdir -p .tools
  curl -L --fail https://micro.mamba.pm/api/micromamba/linux-64/latest -o .tools/micromamba.tar.bz2
  tar -xjf .tools/micromamba.tar.bz2 -C .tools bin/micromamba
  .tools/bin/micromamba create -y -p "$PWD/.tools/env" -c conda-forge python=3.12 cxx-compiler cmake ninja make pkg-config pip
  source scripts/env.sh
fi
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
if [[ ! -d "$NS3_DIR" ]]; then
  mkdir -p "$(dirname "$NS3_DIR")"
  git clone --depth 1 --branch ns-3.45 https://github.com/nsnam/ns-3-dev-git.git "$NS3_DIR"
fi
bash scripts/build.sh
