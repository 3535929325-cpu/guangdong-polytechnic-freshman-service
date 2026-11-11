"""
Build neuron-factory assets: courier, word boxes, neuron agents, conveyor, cranial hall.
Run: blender --background --python blender/scripts/01_build_assets.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from common import (  # noqa: E402
    BLEND_OUT,
    GLB_DIR,
    REFS,
    ROOT,
    assign,
    capsule,
    clear_scene,
    ensure_collection,
    hex_rgb,
    link,
    load_story,
    make_principled,
    set_smooth,
)


def make_text_texture(name: str, text: str, size=(512, 256), fg=(0.25, 0.18, 0.2, 1), bg=(0.96, 0.93, 0.88, 1)):
    """Create a simple image with baked text via Blender font objects rendered to image is heavy;
    instead embed text as a 3D text object parented to boxes at runtime. This stub stores metadata.
    """
    img = bpy.data.images.new(name=name, width=size[0], height=size[1], alpha=True)
    pixels = [bg[0], bg[1], bg[2], bg[3]] * (size[0] * size[1])
    # soft border
    for y in range(size[1]):
        for x in range(size[0]):
            edge = x < 8 or y < 8 or x >= size[0] - 8 or y >= size[1] - 8
            if edge:
                i = (y * size[0] + x) * 4
                pixels[i : i + 4] = [0.85, 0.78, 0.72, 1.0]
    img.pixels = pixels
    return img


def build_courier(palette: dict, col):
    root = bpy.data.objects.new("Courier", None)
    link(root, col)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.55))
    body = bpy.context.active_object
    body.name = "CourierBody"
    body.scale = (0.55, 0.18, 0.55)
    bpy.ops.object.transform_apply(scale=True)
    # slight bevel feel via subdivision
    mod = body.modifiers.new("bevel", "BEVEL")
    mod.width = 0.02
    mod.segments = 2
    mat = make_principled("CourierBlue", palette["courierBlue"], roughness=0.42)
    assign(body, mat)
    set_smooth(body)
    body.parent = root
    link(body, col)

    for i, x in enumerate((-0.14, 0.14)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(x, -0.12, 0.72), segments=16, ring_count=8)
        eye = bpy.context.active_object
        eye.name = f"CourierEye_{i}"
        assign(eye, make_principled("EyeBlack", "#111111", roughness=0.15))
        eye.parent = root
        link(eye, col)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.018, location=(x - 0.015, -0.175, 0.74), segments=8, ring_count=4)
        hl = bpy.context.active_object
        hl.name = f"CourierEyeHL_{i}"
        assign(hl, make_principled("EyeHL", "#FFFFFF", roughness=0.1, emission=(1, 1, 1, 0.4)))
        hl.parent = root
        link(hl, col)

    # logo disc
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.02, location=(0, -0.19, 0.48))
    logo = bpy.context.active_object
    logo.name = "CourierLogo"
    logo.rotation_euler = (math.radians(90), 0, 0)
    assign(logo, make_principled("LogoWhite", "#FFFFFF", roughness=0.35))
    logo.parent = root
    link(logo, col)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(0, -0.205, 0.48), segments=12, ring_count=6)
    spark = bpy.context.active_object
    spark.name = "CourierSpark"
    assign(spark, make_principled("Spark", palette["amber"], roughness=0.3, emission=(*hex_rgb(palette["amber"]), 2.0)))
    spark.parent = root
    link(spark, col)

    for side, sx in (("L", -0.42), ("R", 0.42)):
        arm = capsule(f"CourierArm_{side}", 0.045, 0.18, location=(sx * 0.55, 0.0, 0.45))
        assign(arm, make_principled("ArmBlack", "#1A1A1A", roughness=0.5))
        arm.parent = root
        link(arm, col)
        hand = capsule(f"CourierHand_{side}", 0.09, 0.22, location=(sx, 0.05, 0.35))
        assign(hand, make_principled("HandWhite", "#FFFFFF", roughness=0.4))
        hand.parent = root
        link(hand, col)

    for side, sx in (("L", -0.18), ("R", 0.18)):
        foot = capsule(f"CourierFoot_{side}", 0.1, 0.28, location=(sx, 0.05, 0.1))
        foot.rotation_euler = (0, 0, math.radians(90))
        bpy.ops.object.transform_apply(rotation=True)
        assign(foot, make_principled("FootWhite", "#FFFFFF", roughness=0.4))
        foot.parent = root
        link(foot, col)

    # optional face texture from ref
    logo_path = REFS / "courier-character.png"
    if logo_path.exists():
        try:
            img = bpy.data.images.load(str(logo_path))
            mat = make_principled("CourierFaceTex", palette["courierBlue"], roughness=0.42)
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            tex = nodes.new("ShaderNodeTexImage")
            tex.image = img
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            # keep solid blue body; texture reserved for export metadata
            body["ref_image"] = str(logo_path)
        except Exception:
            pass

    return root


def build_word_box(name: str, label: str, palette: dict, location, col):
    root = bpy.data.objects.new(name, None)
    root.location = location
    link(root, col)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.18))
    box = bpy.context.active_object
    box.name = f"{name}_Mesh"
    box.scale = (0.55, 0.35, 0.18)
    bpy.ops.object.transform_apply(scale=True)
    mod = box.modifiers.new("bevel", "BEVEL")
    mod.width = 0.03
    mod.segments = 3
    assign(box, make_principled(f"{name}_Mat", palette["cream"], roughness=0.65, subsurface=0.15))
    set_smooth(box)
    box.parent = root
    link(box, col)

    bpy.ops.object.text_add(location=(0, -0.2, 0.22))
    txt = bpy.context.active_object
    txt.name = f"{name}_Label"
    txt.data.body = label
    txt.data.size = 0.12
    txt.data.align_x = "CENTER"
    txt.data.align_y = "CENTER"
    txt.data.extrude = 0.01
    txt.rotation_euler = (math.radians(90), 0, 0)
    assign(txt, make_principled(f"{name}_Ink", "#3A2A30", roughness=0.5))
    txt.parent = root
    link(txt, col)
    root["word_label"] = label
    return root


def build_neuron_agent(name: str, label: str, color: str, location, palette: dict, col, hero=False):
    root = bpy.data.objects.new(name, None)
    root.location = location
    link(root, col)

    scale = 1.15 if hero else 0.75
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55 * scale, location=(0, 0, 0.7 * scale), segments=32, ring_count=16)
    body = bpy.context.active_object
    body.name = f"{name}_Body"
    assign(body, make_principled(f"{name}_BodyMat", color, roughness=0.48, subsurface=0.35))
    set_smooth(body)
    body.parent = root
    link(body, col)

    for i, x in enumerate((-0.18 * scale, 0.18 * scale)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12 * scale, location=(x, -0.45 * scale, 0.85 * scale), segments=16, ring_count=8)
        eye = bpy.context.active_object
        eye.name = f"{name}_EyeWhite_{i}"
        assign(eye, make_principled("EyeWhite", "#FFFFFF", roughness=0.3))
        eye.parent = root
        link(eye, col)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05 * scale, location=(x, -0.55 * scale, 0.85 * scale), segments=12, ring_count=6)
        pupil = bpy.context.active_object
        pupil.name = f"{name}_Pupil_{i}"
        assign(pupil, make_principled("Pupil", "#1A1218", roughness=0.2))
        pupil.parent = root
        link(pupil, col)

    # dendrites as thin capsules
    for i, ang in enumerate(range(0, 360, 45)):
        rad = math.radians(ang)
        tip = Vector((math.cos(rad) * 0.9 * scale, math.sin(rad) * 0.55 * scale, 1.35 * scale))
        dend = capsule(f"{name}_Dend_{i}", 0.035 * scale, 0.7 * scale, location=tuple(tip * 0.55 + Vector((0, 0, 0.7 * scale))))
        dend.rotation_euler = (0.4, 0, rad)
        assign(dend, make_principled(f"{name}_DendMat", color, roughness=0.55, subsurface=0.2))
        dend.parent = root
        link(dend, col)

    # nameplate
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.5 * scale, 0.55 * scale))
    plate = bpy.context.active_object
    plate.name = f"{name}_Plate"
    plate.scale = (0.45 * scale, 0.04, 0.14 * scale)
    bpy.ops.object.transform_apply(scale=True)
    assign(plate, make_principled(f"{name}_PlateMat", palette["cream"], roughness=0.5))
    plate.parent = root
    link(plate, col)

    bpy.ops.object.text_add(location=(0, -0.55 * scale, 0.52 * scale))
    txt = bpy.context.active_object
    txt.name = f"{name}_Label"
    txt.data.body = label
    txt.data.size = 0.08 * scale
    txt.data.align_x = "CENTER"
    txt.data.extrude = 0.008
    txt.rotation_euler = (math.radians(90), 0, 0)
    assign(txt, make_principled(f"{name}_LabelInk", "#3A2A30", roughness=0.45))
    txt.parent = root
    link(txt, col)

    # synapse tip empty for growth animation
    tip_empty = bpy.data.objects.new(f"{name}_SynapseTip", None)
    tip_empty.location = (0.0, 0.0, 0.2)
    tip_empty.parent = root
    link(tip_empty, col)

    root["agent_label"] = label
    root["hero"] = hero
    return root


def build_conveyor(palette: dict, col):
    # spiral-ish path using a bezier circle deformed
    curve_data = bpy.data.curves.new("ConveyorPath", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 64
    spline = curve_data.splines.new("NURBS")
    points = []
    for i in range(48):
        t = i / 47.0
        ang = t * math.pi * 2.4
        r = 3.2 - t * 1.2
        x = math.cos(ang) * r
        y = math.sin(ang) * r * 0.55
        z = 0.15 + math.sin(t * math.pi * 2) * 0.15 + t * 0.4
        points.append((x, y, z))
    spline.points.add(len(points) - 1)
    for i, p in enumerate(points):
        spline.points[i].co = (*p, 1.0)
    spline.use_endpoint_u = True
    path_obj = bpy.data.objects.new("ConveyorPath", curve_data)
    link(path_obj, col)

    # belt mesh as thick tube along path
    belt_curve = curve_data.copy()
    belt_curve.bevel_depth = 0.18
    belt_curve.bevel_resolution = 4
    belt_curve.extrude = 0.22
    belt = bpy.data.objects.new("ConveyorBelt", belt_curve)
    assign(belt, make_principled("FleshBelt", palette["flesh"], roughness=0.7, subsurface=0.25))
    link(belt, col)

    return path_obj, belt


def build_environment(palette: dict, col):
    # cranial dome (inverted icosphere shell feeling via scaled sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=18, location=(0, 0, 4), segments=48, ring_count=24)
    dome = bpy.context.active_object
    dome.name = "CranialDome"
    dome.scale = (1.0, 0.85, 0.7)
    # flip normals by negative scale then apply? keep as backdrop with backface
    mat = make_principled("DomeFlesh", "#E5C2BC", roughness=0.85, subsurface=0.4)
    assign(dome, mat)
    # make slightly emissive warm ambient
    # floor fog plane
    link(dome, col)

    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "FactoryFloor"
    assign(floor, make_principled("Floor", "#D8B8B0", roughness=0.9))
    link(floor, col)

    # neural tubes
    for i in range(18):
        ang = i / 18 * math.pi * 2
        r = 7 + (i % 3) * 1.2
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.45 + (i % 4) * 0.08,
            depth=10,
            location=(math.cos(ang) * r, math.sin(ang) * r * 0.7, 5 + (i % 5)),
        )
        tube = bpy.context.active_object
        tube.name = f"NerveTube_{i}"
        tube.rotation_euler = (math.radians(70), 0, ang)
        assign(tube, make_principled(f"Tube_{i}", "#E8B8C4" if i % 2 == 0 else "#D9C0E0", roughness=0.75, subsurface=0.3))
        set_smooth(tube)
        link(tube, col)

    # gate at entrance
    bpy.ops.mesh.primitive_torus_add(major_radius=2.2, minor_radius=0.18, location=(0, 6.5, 1.6))
    gate = bpy.context.active_object
    gate.name = "BrainGate"
    gate.rotation_euler = (math.radians(90), 0, 0)
    assign(gate, make_principled("Gate", "#F0C8C0", roughness=0.5, emission=(*hex_rgb("#FFD0C8"), 0.35)))
    link(gate, col)
    return dome


def build_dendrite_arm(palette: dict, col):
    root = bpy.data.objects.new("DendriteArm", None)
    root.location = (0.5, -0.2, 4.2)
    link(root, col)
    segments = []
    for i in range(5):
        seg = capsule(f"ArmSeg_{i}", 0.08 - i * 0.008, 0.7, location=(0.2 * i, 0.1 * i, -0.55 * i))
        assign(seg, make_principled(f"ArmSegMat_{i}", palette["neuronPink"], roughness=0.5, subsurface=0.3))
        seg.parent = root if i == 0 else segments[i - 1]
        if i > 0:
            seg.location = (0.05, 0.0, -0.55)
        link(seg, col)
        segments.append(seg)
    hand = capsule("ArmHand", 0.12, 0.28, location=(0.05, 0.0, -0.55))
    assign(hand, make_principled("ArmHandMat", palette["neuronPink"], roughness=0.45, subsurface=0.25))
    hand.parent = segments[-1]
    link(hand, col)
    target = bpy.data.objects.new("ArmIKTarget", None)
    target.location = (1.0, 0.8, 0.8)
    link(target, col)
    return root, target


def build_synapses(palette: dict, col, agent_a, agent_b):
    curve_data = bpy.data.curves.new("SynapseA", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = 0.04
    curve_data.bevel_resolution = 3
    curve_data.bevel_factor_end = 0.0
    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(1)
    p0, p1 = spline.bezier_points
    p0.co = agent_a.location + Vector((0.3, 0, 0.6))
    p1.co = (agent_a.location + agent_b.location) / 2 + Vector((0, 0, 0.4))
    for p in (p0, p1):
        p.handle_left_type = "AUTO"
        p.handle_right_type = "AUTO"
    syn_a = bpy.data.objects.new("SynapseA", curve_data)
    assign(syn_a, make_principled("SynA", palette["neuronPink"], roughness=0.4, emission=(*hex_rgb(palette["neuronPink"]), 0.8)))
    link(syn_a, col)

    curve_data_b = curve_data.copy()
    curve_data_b.bevel_factor_end = 0.0
    syn_b = bpy.data.objects.new("SynapseB", curve_data_b)
    # retarget endpoints later in animate
    assign(syn_b, make_principled("SynB", palette["amber"], roughness=0.4, emission=(*hex_rgb(palette["amber"]), 0.8)))
    link(syn_b, col)

    for name, loc in (("HandA", agent_a.location + Vector((0.8, 0, 0.5)),), ("HandB", agent_b.location + Vector((-0.8, 0, 0.5)),)):
        pass
    hand_a = capsule("SynapseHandA", 0.1, 0.22, location=tuple(agent_a.location + Vector((0.9, 0, 0.55))))
    assign(hand_a, make_principled("HandA", palette["warmWhite"], roughness=0.35, emission=(*hex_rgb(palette["warmWhite"]), 0.2)))
    link(hand_a, col)
    hand_b = capsule("SynapseHandB", 0.1, 0.22, location=tuple(agent_b.location + Vector((-0.9, 0, 0.55))))
    assign(hand_b, make_principled("HandB", palette["warmWhite"], roughness=0.35, emission=(*hex_rgb(palette["warmWhite"]), 0.2)))
    link(hand_b, col)
    return syn_a, syn_b, hand_a, hand_b


def setup_world(palette: dict):
    world = bpy.data.worlds.new("FactoryWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (*hex_rgb("#2A1F28"), 1)
    bg.inputs["Strength"].default_value = 0.35
    links.new(bg.outputs["Background"], out.inputs["Surface"])

    # key lights
    bpy.ops.object.light_add(type="AREA", location=(4, -6, 8))
    key = bpy.context.active_object
    key.name = "KeyLight"
    key.data.energy = 250
    key.data.size = 8
    key.data.color = hex_rgb("#FFE6DC")

    bpy.ops.object.light_add(type="AREA", location=(-6, 4, 6))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = 120
    fill.data.size = 10
    fill.data.color = hex_rgb("#D8E8FF")

    bpy.ops.object.light_add(type="POINT", location=(0, 0, 3))
    rim = bpy.context.active_object
    rim.name = "HeartLight"
    rim.data.energy = 80
    rim.data.color = hex_rgb("#FFC8C0")


def export_glb():
    GLB_DIR.mkdir(parents=True, exist_ok=True)
    out = GLB_DIR / "factory_pack.glb"
    bpy.ops.export_scene.gltf(filepath=str(out), export_format="GLB", use_selection=False)
    print(f"Exported {out}")


def main():
    story = load_story()
    palette = story["palette"]
    clear_scene()
    setup_world(palette)

    env_col = ensure_collection("Environment")
    actors_col = ensure_collection("Actors")
    props_col = ensure_collection("Props")

    build_environment(palette, env_col)
    path_obj, _belt = build_conveyor(palette, env_col)

    courier = build_courier(palette, actors_col)
    courier.location = (0, 5.5, 0.35)

    boxes = []
    labels = [story["words"]["form"], *story["words"]["background"]]
    for i, label in enumerate(labels):
        ang = i / max(1, len(labels)) * math.pi * 1.6
        loc = (math.cos(ang) * 2.6, math.sin(ang) * 1.4, 0.35 + i * 0.05)
        box = build_word_box(f"WordBox_{i}", label, palette, loc, props_col)
        boxes.append(box)

    agent_form = build_neuron_agent(
        "AgentForm",
        story["words"]["form"],
        palette["neuronPink"],
        (1.4, -0.6, 0.0),
        palette,
        actors_col,
        hero=True,
    )
    agent_meaning = build_neuron_agent(
        "AgentMeaning",
        story["words"]["meaning"],
        palette["neuronBlue"],
        (-1.5, -1.0, 0.0),
        palette,
        actors_col,
        hero=True,
    )

    # crowd agents
    for i in range(40):
        ang = i / 40 * math.pi * 2
        r = 4.5 + (i % 5) * 0.7
        loc = (math.cos(ang) * r, math.sin(ang) * r * 0.65 - 2.0, 0.0)
        color = palette["neuronPink"] if i % 2 == 0 else palette["neuronBlue"]
        label = story["words"]["background"][i % len(story["words"]["background"])]
        build_neuron_agent(f"Crowd_{i}", label, color, loc, palette, actors_col, hero=False)

    build_dendrite_arm(palette, actors_col)
    build_synapses(palette, props_col, agent_form, agent_meaning)

    # camera placeholder
    bpy.ops.object.camera_add(location=(2.2, 1.4, 6.5))
    cam = bpy.context.active_object
    cam.name = "StoryCamera"
    bpy.context.scene.camera = cam
    cam.data.lens = 35
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 4.0
    cam.data.dof.aperture_fstop = 2.8

    BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
    export_glb()
    print(f"Saved {BLEND_OUT}")
    print("01_build_assets.py complete")


if __name__ == "__main__":
    main()
