"""
Render neuron factory story with EEVEE to MP4/PNG sequence.
Run: blender --background --python blender/scripts/03_render_eevee.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import bpy

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from common import BLEND_OUT, FINAL_DIR, frame_of, load_story  # noqa: E402


def main():
    story = load_story()
    if not BLEND_OUT.exists():
        raise SystemExit(f"Missing {BLEND_OUT}; run 01 then 02 first")
    bpy.ops.wm.open_mainfile(filepath=str(BLEND_OUT))

    fps = int(story.get("fps", 24))
    w, h = story.get("resolution", [1920, 1080])
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys() else "BLENDER_EEVEE"
    # fallback if enum check awkward
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"

    scene.render.resolution_x = w
    scene.render.resolution_y = h
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = frame_of(story["duration"], fps)
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"

    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    out = FINAL_DIR / "neuron_factory.mp4"
    scene.render.filepath = str(out)

    # EEVEE quality knobs when available
    eevee = getattr(scene, "eevee", None)
    if eevee:
        if hasattr(eevee, "taa_render_samples"):
            eevee.taa_render_samples = 64
        if hasattr(eevee, "use_bloom"):
            eevee.use_bloom = True
            eevee.bloom_intensity = 0.05
        if hasattr(eevee, "use_gtao"):
            eevee.use_gtao = True

    print(f"Rendering {scene.frame_start}-{scene.frame_end} -> {out}")
    bpy.ops.render.render(animation=True)
    print("03_render_eevee.py complete")


if __name__ == "__main__":
    main()
