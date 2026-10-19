#!/usr/bin/env bash
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -d "$PROJECT_ROOT/.tools/env" ]]; then
  export PATH="$PROJECT_ROOT/.tools/env/bin:$PATH"
  export CC="$PROJECT_ROOT/.tools/env/bin/x86_64-conda-linux-gnu-cc"
  export CXX="$PROJECT_ROOT/.tools/env/bin/x86_64-conda-linux-gnu-c++"
fi
export NS3_DIR="${NS3_DIR:-$PROJECT_ROOT/vendor/ns-3.45}"
