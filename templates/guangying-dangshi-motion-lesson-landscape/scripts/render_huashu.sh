#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
REPO="${HUASHU_REPO:-third_party/huashu-art-motion}"
if [[ ! -f "$REPO/scripts/engine/render.py" ]]; then
  echo "Huashu source not found at $REPO. Install: git clone https://github.com/alchaincyf/huashu-art-motion.git $REPO" >&2
  exit 2
fi
command -v uv >/dev/null || { echo 'Install uv: https://docs.astral.sh/uv/' >&2; exit 2; }
command -v ffmpeg >/dev/null || { echo 'FFmpeg required' >&2; exit 2; }
mkdir -p media/huashu
for file in huashu-specs/*.json; do
  b="$(basename "$file" .json)"
  echo "Rendering $b via huashu-art-motion ..."
  uv run --with playwright python "$REPO/scripts/engine/render.py" --spec "$PWD/$file" --out "$PWD/media/huashu/$b.mp4"
done
python3 scripts/build_composition.py
