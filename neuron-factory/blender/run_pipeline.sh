#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BLENDER="${BLENDER:-blender}"

"$BLENDER" --background --python blender/scripts/01_build_assets.py
"$BLENDER" --background --python blender/scripts/02_animate_story.py
"$BLENDER" --background --python blender/scripts/03_render_eevee.py
echo "Pipeline complete -> exports/final/neuron_factory.mp4"
