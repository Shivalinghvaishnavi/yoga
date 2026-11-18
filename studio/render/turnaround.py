"""Render character turnaround + close-ups from instructor.blend.

Run:  blender -b studio/character/instructor.blend -P studio/render/turnaround.py -- <out_dir> [views...]
"""
import math
import os
import sys
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "/tmp/yf_turn"
ONLY = set(argv[1:])
os.makedirs(OUT, exist_ok=True)

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 32
sc.view_settings.view_transform = "Standard"
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.compression = 90
sc.world = bpy.data.worlds.new("W")
sc.world.use_nodes = True
bg = sc.world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.62, 0.66, 0.68, 1)
bg.inputs[1].default_value = 0.55

# floor
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
fl = bpy.context.object
fm = bpy.data.materials.new("Floor"); fm.use_nodes = True
fm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.78, 0.77, 0.74, 1)
fl.data.materials.append(fm)

def light(kind, loc, energy, size=2.0, color=(1, 1, 1)):
    d = bpy.data.lights.new(kind, kind)
    d.energy = energy; d.color = color
    if kind == "AREA": d.size = size
    o = bpy.data.objects.new(kind, d); o.location = loc
    sc.collection.objects.link(o)
    t = o.constraints.new("TRACK_TO"); t.track_axis = "TRACK_NEGATIVE_Z"; t.up_axis = "UP_Y"
    tgt = bpy.data.objects.new("T", None); tgt.location = (0, 0, 1.0); sc.collection.objects.link(tgt)
    t.target = tgt

light("AREA", (-2.5, -3.0, 3.0), 300, 3.0, (1.0, 0.96, 0.9))
light("AREA", (3.0, -2.0, 1.6), 110, 3.0, (0.9, 0.95, 1.0))
light("AREA", (0.5, 3.0, 2.5), 180, 2.0)

cam_d = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam

def shot(name, loc, target, res, ortho=None, lens=85):
    if ONLY and name not in ONLY: return
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam_d.type = "ORTHO"; cam_d.ortho_scale = ortho
    else:
        cam_d.type = "PERSP"; cam_d.lens = lens
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)

shot("front", (0, -8, 0.85), (0, 0, 0.85), (720, 1080), ortho=1.9)
shot("side", (8, 0, 0.85), (0, 0, 0.85), (720, 1080), ortho=1.9)
shot("back", (0, 8, 0.85), (0, 0, 0.85), (720, 1080), ortho=1.9)
shot("face", (0.25, -0.85, 1.58), (0, -0.05, 1.54), (900, 900), lens=85)
shot("face_side", (0.8, -0.35, 1.56), (0, -0.02, 1.54), (900, 900), lens=85)
shot("outfit", (0, -2.2, 1.12), (0, 0, 1.08), (900, 900), ortho=0.95)
shot("wrists", (0, -3, 0.95), (0, 0, 0.95), (900, 600), ortho=1.2)
shot("shoes", (0.55, -0.7, 0.35), (0.0, -0.05, 0.07), (900, 700), lens=60)
