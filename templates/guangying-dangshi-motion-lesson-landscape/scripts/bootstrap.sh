#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
node --version
npm install
python3 scripts/build_data.py
python3 scripts/validate.py
if [[ ! -f third_party/huashu-art-motion/SKILL.md ]]; then
 mkdir -p third_party
 git clone --depth 1 https://github.com/alchaincyf/huashu-art-motion.git third_party/huashu-art-motion
fi
cat <<'MSG'
Bootstrapped! Run:
  python3 -m http.server 8765
  Open http://localhost:8765/preview.html
For Huashu clips: bash scripts/render_huashu.sh
For HyperFrames render: npx hyperframes lint && npx hyperframes check && npx hyperframes render --output output/ep01.mp4
MSG
