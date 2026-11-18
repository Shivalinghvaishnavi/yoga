"""Render a few still frames of a motion for quick visual checks.

blender -b studio/character/instructor_mpfb.blend -P studio/render/preview.py -- <motion> <camera> <outprefix> <t1,t2,...> [WxH]
Writes <outprefix>_<n>.png. Add __R to the motion name for the mirrored version.
"""
import importlib
import os
import sys
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "motions"), os.path.join(ROOT, "render")]
import rigkit, stage, props, lib  # noqa: E402

motion, camname, prefix, times = sys.argv[sys.argv.index("--") + 1:][:4]
res = tuple(int(v) for v in sys.argv[-1].split("x")) if sys.argv[-1][0].isdigit() and "x" in sys.argv[-1] else (480, 270)
mirror = motion.endswith("__R")
mod = lib.load(motion)
cam = stage.setup(res, samples=8)
stage.aim(cam, getattr(mod, 'CAM', 'front34') if camname == 'auto' else camname, mirror)
if getattr(mod, 'PROPS', None):
    mod.PROPS(props, mirror)
rig = rigkit.Rig(bpy.data.objects["Human.rig"])
band = None
if getattr(mod, "BAND", False):
    import band_prop
    band = band_prop.Band()
for n, t in enumerate(float(x) for x in times.split(",")):
    p = mod.pose(t)
    rig.solve(rigkit.mirror_pose(p) if mirror else p)
    if getattr(mod, 'GROUND', False):
        rigkit.ground(rig)
    if band:
        band.update(rig, 1 + n, mod.band_anchor(rig, t) if hasattr(mod, "band_anchor") else None)
        bpy.context.scene.frame_set(1 + n)
    bpy.context.scene.render.filepath = f"{prefix}_{n}.png"
    bpy.ops.render.render(write_still=True)
print("PREVIEW", motion, times)
