#!/usr/bin/env bash

set -euo pipefail

cat <<'EOF'
skill-manager.sh is deprecated.

Phase 3 moved this repository to a Python CLI with canonical-skills as the only public source.

Use one of these instead:

  python3 -m pip install -e .
  python3 -m skill_toolkit --help
  skill-toolkit --help
EOF
