"""Shared helpers for neuron-factory Blender scripts."""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
STORYBOARD = ROOT / "shared" / "storyboard.json"
BLEND_OUT = ROOT / "exports" / "neuron_factory.blend"
GLB_DIR = ROOT / "exports" / "glb"
FINAL_DIR = ROOT / "exports" / "final"
REFS = ROOT / "refs"


def load_story() -> dict:
    with STORYBOARD.open(encoding="utf-8") as f:
        return json.load(f)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.images):
        for item in list(block):
            block.remove(item)


def hex_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def make_principled(
    name: str,
    color: str | tuple[float, float, float],
    *,
    roughness: float = 0.55,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    subsurface: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    rgb = hex_rgb(color) if isinstance(color, str) else color
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = subsurface
    if emission:
        strength = emission[3]
        color4 = (emission[0], emission[1], emission[2], 1.0)
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = color4
            bsdf.inputs["Emission Strength"].default_value = strength
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (*color4[:3], 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = strength
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def assign(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def set_smooth(obj: bpy.types.Object) -> None:
    for poly in obj.data.polygons:
        poly.use_smooth = True


def frame_of(seconds: float, fps: int = 24) -> int:
    return int(round(seconds * fps)) + 1


def ensure_collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def link(obj: bpy.types.Object, collection: bpy.types.Collection | None = None) -> None:
    if collection is None:
        collection = bpy.context.scene.collection
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    # unlink from scene root duplicates if needed
    for col in list(obj.users_collection):
        if col != collection:
            col.objects.unlink(obj)


def capsule(name: str, radius: float, depth: float, location=(0, 0, 0)) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=24, ring_count=12)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (1.0, depth / (radius * 2.0), 1.0)
    bpy.ops.object.transform_apply(scale=True)
    set_smooth(obj)
    return obj
