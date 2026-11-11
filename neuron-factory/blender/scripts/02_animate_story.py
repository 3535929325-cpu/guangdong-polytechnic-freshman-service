"""
Animate 75s story from shared/storyboard.json onto exports/neuron_factory.blend.
Run: blender --background --python blender/scripts/02_animate_story.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from common import BLEND_OUT, frame_of, load_story  # noqa: E402


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def shot_at(story, t: float):
    for shot in story["shots"]:
        if shot["start"] <= t <= shot["end"] or (t >= shot["start"] and t < shot["end"]):
            return shot
    return story["shots"][-1]


def camera_pose(shot, t: float):
    span = max(0.001, shot["end"] - shot["start"])
    u = smoothstep((t - shot["start"]) / span)
    frm = shot["camera"]["from"]
    to = shot["camera"]["to"]
    pos = [lerp(frm["pos"][i], to["pos"][i], u) for i in range(3)]
    target = [lerp(frm["target"][i], to["target"][i], u) for i in range(3)]
    if shot["camera"].get("orbit"):
        ang = (t - shot["start"]) * 0.18
        radius = 5.2
        pos = [math.sin(ang) * radius, 2.4, math.cos(ang) * radius]
    return pos, target


def look_at(cam: bpy.types.Object, target: Vector):
    direction = target - cam.location
    rot = direction.to_track_quat("-Z", "Y")
    cam.rotation_euler = rot.to_euler()


def key_obj_loc(obj, frame, loc):
    obj.location = loc
    obj.keyframe_insert(data_path="location", frame=frame)


def key_obj_rot(obj, frame, rot):
    obj.rotation_euler = rot
    obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def ensure_open():
    if BLEND_OUT.exists():
        bpy.ops.wm.open_mainfile(filepath=str(BLEND_OUT))
    else:
        raise SystemExit(f"Missing {BLEND_OUT}; run 01_build_assets.py first")


def animate_courier(story, fps):
    courier = bpy.data.objects.get("Courier")
    if not courier:
        return
    # ride conveyor entrance then settle near form box
    path = [
        (0.0, (0.0, 6.2, 0.4)),
        (4.0, (0.3, 4.0, 0.45)),
        (8.0, (0.6, 2.2, 0.5)),
        (15.0, (1.0, 1.0, 0.55)),
        (25.0, (1.2, 0.6, 0.55)),
        (75.0, (1.2, 0.4, 0.55)),
    ]
    for t, loc in path:
        key_obj_loc(courier, frame_of(t, fps), Vector(loc))
        # gentle bob
        key_obj_rot(courier, frame_of(t, fps), Euler((0.05 * math.sin(t), 0, 0.1 * math.sin(t * 0.7))))


def animate_boxes(story, fps):
    for i in range(6):
        box = bpy.data.objects.get(f"WordBox_{i}")
        if not box:
            continue
        for t in range(0, int(story["duration"]) + 1, 2):
            ang = (i / 6) * math.pi * 1.6 + t * 0.12
            r = 2.6 - (t / story["duration"]) * 0.3
            loc = Vector((math.cos(ang) * r, math.sin(ang) * r * 0.55, 0.35 + 0.05 * math.sin(t + i)))
            # lock form box near agent during assign
            if i == 0 and t >= 26:
                loc = Vector((1.35, -0.2, 0.9 if t < 31 else 1.15))
            key_obj_loc(box, frame_of(t, fps), loc)


def animate_arm(story, fps):
    arm = bpy.data.objects.get("DendriteArm")
    target = bpy.data.objects.get("ArmIKTarget")
    hand = bpy.data.objects.get("ArmHand")
    if not arm:
        return
    # grab form
    key_obj_loc(arm, frame_of(24, fps), Vector((0.5, -0.2, 4.2)))
    key_obj_loc(arm, frame_of(27, fps), Vector((1.0, 0.2, 2.0)))
    key_obj_loc(arm, frame_of(31, fps), Vector((1.3, -0.4, 1.6)))
    key_obj_loc(arm, frame_of(34, fps), Vector((0.8, -0.5, 2.4)))
    # grab meaning
    key_obj_loc(arm, frame_of(43, fps), Vector((-0.4, -0.2, 3.8)))
    key_obj_loc(arm, frame_of(46, fps), Vector((-1.0, 0.1, 2.0)))
    key_obj_loc(arm, frame_of(49, fps), Vector((-1.4, -0.7, 1.5)))
    key_obj_loc(arm, frame_of(52, fps), Vector((-0.6, -0.4, 2.5)))
    if target:
        key_obj_loc(target, frame_of(27, fps), Vector((1.2, 0.8, 0.8)))
        key_obj_loc(target, frame_of(31, fps), Vector((1.4, -0.4, 1.2)))
        key_obj_loc(target, frame_of(46, fps), Vector((-1.1, 0.5, 0.8)))
        key_obj_loc(target, frame_of(49, fps), Vector((-1.5, -0.8, 1.1)))
    if hand:
        for f in (frame_of(30.5, fps), frame_of(48.5, fps)):
            hand.scale = (1.2, 1.2, 1.2)
            hand.keyframe_insert("scale", frame=f)
            hand.scale = (1.0, 1.0, 1.0)
            hand.keyframe_insert("scale", frame=f + 8)


def animate_agents(story, fps):
    form = bpy.data.objects.get("AgentForm")
    meaning = bpy.data.objects.get("AgentMeaning")
    if form:
        # plate glow via scale punch when assigned
        form.scale = (1, 1, 1)
        form.keyframe_insert("scale", frame=frame_of(29, fps))
        form.scale = (1.12, 1.12, 1.12)
        form.keyframe_insert("scale", frame=frame_of(31, fps))
        form.scale = (1, 1, 1)
        form.keyframe_insert("scale", frame=frame_of(33, fps))
    if meaning:
        meaning.scale = (1, 1, 1)
        meaning.keyframe_insert("scale", frame=frame_of(47, fps))
        meaning.scale = (1.12, 1.12, 1.12)
        meaning.keyframe_insert("scale", frame=frame_of(49, fps))
        meaning.scale = (1, 1, 1)
        meaning.keyframe_insert("scale", frame=frame_of(51, fps))


def animate_synapses(story, fps):
    syn_a = bpy.data.objects.get("SynapseA")
    syn_b = bpy.data.objects.get("SynapseB")
    hand_a = bpy.data.objects.get("SynapseHandA")
    hand_b = bpy.data.objects.get("SynapseHandB")
    form = bpy.data.objects.get("AgentForm")
    meaning = bpy.data.objects.get("AgentMeaning")
    if not (syn_a and syn_b and form and meaning):
        return

    # update curve endpoints
    mid = (form.location + meaning.location) / 2 + Vector((0, 0, 0.8))
    for syn, start, end in (
        (syn_a, form.location + Vector((0.4, 0, 0.7)), mid),
        (syn_b, meaning.location + Vector((-0.4, 0, 0.7)), mid),
    ):
        spline = syn.data.splines[0]
        if spline.type == "BEZIER":
            spline.bezier_points[0].co = start
            spline.bezier_points[-1].co = end

    # grow bevel_factor_end over S07
    for syn in (syn_a, syn_b):
        syn.data.bevel_factor_end = 0.0
        syn.data.keyframe_insert("bevel_factor_end", frame=frame_of(52, fps))
        syn.data.bevel_factor_end = 1.0
        syn.data.keyframe_insert("bevel_factor_end", frame=frame_of(65, fps))

    # hands move to meet
    if hand_a and hand_b:
        key_obj_loc(hand_a, frame_of(52, fps), form.location + Vector((0.6, 0, 0.55)))
        key_obj_loc(hand_b, frame_of(52, fps), meaning.location + Vector((-0.6, 0, 0.55)))
        key_obj_loc(hand_a, frame_of(65, fps), mid + Vector((-0.12, 0, 0)))
        key_obj_loc(hand_b, frame_of(65, fps), mid + Vector((0.12, 0, 0)))
        # flash scale
        for hand in (hand_a, hand_b):
            hand.scale = (1, 1, 1)
            hand.keyframe_insert("scale", frame=frame_of(64.5, fps))
            hand.scale = (1.6, 1.6, 1.6)
            hand.keyframe_insert("scale", frame=frame_of(66, fps))
            hand.scale = (1.15, 1.15, 1.15)
            hand.keyframe_insert("scale", frame=frame_of(68, fps))

    # heart light boost
    heart = bpy.data.objects.get("HeartLight")
    if heart:
        heart.data.energy = 80
        heart.data.keyframe_insert("energy", frame=frame_of(64, fps))
        heart.data.energy = 320
        heart.data.keyframe_insert("energy", frame=frame_of(66, fps))
        heart.data.energy = 140
        heart.data.keyframe_insert("energy", frame=frame_of(70, fps))


def animate_camera(story, fps):
    cam = bpy.data.objects.get("StoryCamera")
    if not cam:
        return
    duration = story["duration"]
    for t_i in range(0, int(duration * fps) + 1, 2):
        t = t_i / fps
        shot = shot_at(story, t)
        pos, target = camera_pose(shot, t)
        cam.location = Vector(pos)
        cam.keyframe_insert("location", frame=t_i + 1)
        look_at(cam, Vector(target))
        cam.keyframe_insert("rotation_euler", frame=t_i + 1)
        if cam.data.dof:
            cam.data.dof.focus_distance = (Vector(pos) - Vector(target)).length
            cam.data.dof.keyframe_insert("focus_distance", frame=t_i + 1)


def setup_timeline(story, fps):
    scene = bpy.context.scene
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = frame_of(story["duration"], fps)
    scene.frame_current = 1


def main():
    story = load_story()
    fps = int(story.get("fps", 24))
    ensure_open()
    setup_timeline(story, fps)
    animate_courier(story, fps)
    animate_boxes(story, fps)
    animate_arm(story, fps)
    animate_agents(story, fps)
    animate_synapses(story, fps)
    animate_camera(story, fps)
    bpy.ops.wm.save_mainfile()
    print("02_animate_story.py complete")


if __name__ == "__main__":
    main()
