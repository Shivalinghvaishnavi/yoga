"""Shared Blender helpers for the YogaFlow instructor build (Blender 5.x).

Coordinate convention: Z up, character faces -Y, her LEFT side is +X
(so in a front camera at -Y she appears with her left on screen right).
"""
import bpy
import bmesh
import math
from mathutils import Vector, Quaternion

PALETTE = {
    "skin":     (0.50, 0.31, 0.21),
    "hair":     (0.07, 0.04, 0.027),
    "teal":     (0.015, 0.32, 0.34),
    "coral":    (0.80, 0.22, 0.17),
    "legging":  (0.045, 0.047, 0.06),
    "white":    (0.85, 0.86, 0.88),
    "sole":     (0.62, 0.63, 0.66),
    "lip":      (0.46, 0.17, 0.16),
    "iris":     (0.10, 0.055, 0.03),
    "eye":      (0.92, 0.91, 0.88),
}


def make_material(name, color, rough=0.5, sss=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    if sss:
        for key in ("Subsurface Weight", "Subsurface"):
            if key in b.inputs:
                b.inputs[key].default_value = sss
                break
        if "Subsurface Radius" in b.inputs:
            b.inputs["Subsurface Radius"].default_value = (0.9, 0.35, 0.25)
    return m


def make_materials():
    P = PALETTE
    return {
        "skin": make_material("Skin", P["skin"], 0.5, 0.08),
        "hair": make_material("Hair", P["hair"], 0.35),
        "teal": make_material("Teal", P["teal"], 0.6),
        "coral": make_material("Coral", P["coral"], 0.6),
        "legging": make_material("Legging", P["legging"], 0.75),
        "white": make_material("ShoeWhite", P["white"], 0.5),
        "sole": make_material("Sole", P["sole"], 0.7),
        "lip": make_material("Lip", P["lip"], 0.35),
        "iris": make_material("Iris", P["iris"], 0.2),
        "eye": make_material("EyeWhite", P["eye"], 0.2),
        "dark": make_material("DarkDetail", (0.02, 0.015, 0.012), 0.5),
    }


def new_collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def finish(name, bm, mat, coll, smooth=True, subsurf=0):
    me = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    if mat is not None:
        me.materials.append(mat)
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if subsurf:
        m = ob.modifiers.new("Subsurf", "SUBSURF")
        m.levels = subsurf
        m.render_levels = subsurf
    return ob


def ellipsoid(name, center, radii, mat, coll, rot=None, segs=24, rings=14, subsurf=0):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    for v in bm.verts:
        p = Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2]))
        if rot is not None:
            p = rot @ p
        v.co = p + Vector(center)
    return finish(name, bm, mat, coll, subsurf=subsurf)


def _catmull(P, R, sub):
    out_p, out_r = [], []
    n = len(P)
    for i in range(n - 1):
        p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, n - 1)]
        for k in range(sub):
            t = k / sub
            t2, t3 = t * t, t * t * t
            out_p.append(0.5 * ((2 * p1) + (-p0 + p2) * t +
                                (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                                (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
            out_r.append(R[i] * (1 - t) + R[i + 1] * t)
    out_p.append(P[-1])
    out_r.append(R[-1])
    return out_p, out_r


def tube(name, pts, radii, mat, coll, sides=10, sub=4, squash=None, subsurf=0):
    P = [Vector(p) for p in pts]
    R = list(radii)
    if len(P) > 2:
        P, R = _catmull(P, R, sub)
    bm = bmesh.new()
    rings = []
    n = len(P)
    for i, p in enumerate(P):
        t = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((0, 1, 0))
        a = t.cross(ref).normalized()
        b = t.cross(a).normalized()
        rings.append([bm.verts.new(p + (a * math.cos(2 * math.pi * k / sides) +
                                        b * math.sin(2 * math.pi * k / sides)) * R[i])
                      for k in range(sides)])
    for i in range(n - 1):
        for k in range(sides):
            k2 = (k + 1) % sides
            bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
    for idx, ring, sgn in ((0, rings[0], -1), (n - 1, rings[-1], 1)):
        t = (P[1] - P[0]).normalized() if idx == 0 else (P[-1] - P[-2]).normalized()
        pole = bm.verts.new(P[idx] + t * sgn * R[idx] * 0.7)
        for k in range(sides):
            bm.faces.new((ring[k], ring[(k + 1) % sides], pole))
    if squash:
        c = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
        for v in bm.verts:
            d = v.co - c
            v.co = c + Vector((d.x * squash[0], d.y * squash[1], d.z * squash[2]))
    return finish(name, bm, mat, coll, subsurf=subsurf)


def bind_rigid(ob, arm, bone):
    vg = ob.vertex_groups.new(name=bone)
    vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
    m = ob.modifiers.new("Armature", "ARMATURE")
    m.object = arm
    ob.parent = arm


def rot_down_to(direction):
    """Quaternion taking local -Z (fingers-down) to `direction`."""
    return Vector((0, 0, -1)).rotation_difference(Vector(direction).normalized())
