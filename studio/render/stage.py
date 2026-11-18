"""Studio set (floor, yoga mat, lights, cameras) shared by clip and turnaround renders."""
import bpy
from mathutils import Vector

CAMS = {
    "front34": ((-1.7, -4.9, 1.15), (0, 0, 0.80), 50),
    "side34": ((4.3, -3.6, 1.15), (0, 0, 0.80), 50),
    "side34L": ((-4.3, -3.6, 1.15), (0, 0, 0.80), 50),
    "sideview": ((5.2, -0.4, 1.15), (0, 0, 0.80), 50),
    "floor_side": ((4.4, 0.1, 0.95), (0, 0, 0.30), 50),
    "floor34": ((3.2, -3.3, 1.5), (0, 0, 0.25), 50),
    "floor_front": ((0.0, -4.2, 1.1), (0, 0, 0.35), 50),
    "close": ((-1.0, -3.0, 1.5), (0, 0, 1.15), 50),
    "profile": ((3.2, 0, 1.45), (0, 0, 1.40), 50),
    "front": ((0, -5.8, 1.2), (0, 0, 0.82), 50),
    "side": ((5.8, 0, 1.2), (0, 0, 0.82), 50),
}


def _mat(name, rgb, rough=0.85):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    return m


def _light(kind, loc, energy, size=3.0, color=(1, 1, 1)):
    d = bpy.data.lights.new(kind, kind)
    d.energy, d.color = energy, color
    if kind == "AREA":
        d.size = size
    o = bpy.data.objects.new(kind, d)
    o.location = loc
    bpy.context.scene.collection.objects.link(o)
    t = bpy.data.objects.new("T", None)
    t.location = (0, 0, 0.9)
    bpy.context.scene.collection.objects.link(t)
    c = o.constraints.new("TRACK_TO")
    c.target, c.track_axis, c.up_axis = t, "TRACK_NEGATIVE_Z", "UP_Y"


def setup(res=(960, 540), samples=24):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = samples
    sc.view_settings.view_transform = "Standard"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.world = bpy.data.worlds.new("W")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value, bg.inputs[1].default_value = (0.80, 0.82, 0.82, 1), 0.6
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
    bpy.context.object.data.materials.append(_mat("Floor", (0.62, 0.58, 0.52), 0.8))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.005))
    mat = bpy.context.object
    mat.scale = (0.72, 1.9, 0.01)
    mat.data.materials.append(_mat("YogaMat", (0.18, 0.30, 0.36), 0.6))
    _light("AREA", (-2.5, -3.0, 3.2), 330, 3.0, (1.0, 0.96, 0.9))
    _light("AREA", (3.0, -2.5, 1.8), 120, 3.0, (0.9, 0.95, 1.0))
    _light("AREA", (0.5, 3.0, 2.5), 200, 2.0)
    cd = bpy.data.cameras.new("Cam")
    cam = bpy.data.objects.new("Cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def aim(cam, preset, mirror=False):
    loc, tgt, lens = CAMS[preset]
    if mirror and preset.endswith("L"):   # camera on the side away from a mirrored wall
        loc = (-loc[0], loc[1], loc[2])
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
