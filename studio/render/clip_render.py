"""Bake a motion module to keyframes and render it as a silent MP4 clip.

blender -b studio/character/instructor_mpfb.blend -P studio/render/clip_render.py -- <motion> <camera> <out.mp4> [WxH]
A motion module defines: FPS, PERIOD (seconds), pose(t_seconds) -> pose dict (see rigkit.Rig.solve).
"""
import importlib
import os
import sys
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "motions"), os.path.join(ROOT, "render")]
import rigkit, stage, props, lib  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
motion, camname, out = argv[:3]
res = tuple(int(v) for v in argv[3].split("x")) if len(argv) > 3 else (960, 540)
mirror = motion.endswith("__R")
mod = lib.load(motion)

cam = stage.setup(res)
stage.aim(cam, getattr(mod, 'CAM', 'front34') if camname == 'auto' else camname, mirror)
if getattr(mod, 'PROPS', None):
    mod.PROPS(props, mirror)
rig = rigkit.Rig(bpy.data.objects["Human.rig"])
band = None
if getattr(mod, "BAND", False):
    import band_prop
    band = band_prop.Band()
sc = bpy.context.scene
FPS = int(os.environ.get('GF_FPS', mod.FPS))
sc.render.fps = FPS
n = int(round(mod.PERIOD * FPS))
sc.frame_start, sc.frame_end = 1, n
for f in range(n):
    rig.solve(rigkit.mirror_pose(mod.pose(f / FPS)) if mirror else mod.pose(f / FPS))
    if getattr(mod, 'GROUND', False):
        rigkit.ground(rig)
    if band:
        band.update(rig, f + 1, mod.band_anchor(rig, f / FPS) if hasattr(mod, "band_anchor") else None)
    for pb in rig.pb:
        pb.keyframe_insert("location", frame=f + 1)
        pb.keyframe_insert("rotation_quaternion", frame=f + 1)
r = sc.render
r.image_settings.media_type = "VIDEO"
r.image_settings.file_format = "FFMPEG"
r.ffmpeg.format, r.ffmpeg.codec = "MPEG4", "H264"
r.ffmpeg.constant_rate_factor, r.ffmpeg.ffmpeg_preset = "HIGH", "GOOD"
r.filepath = out
bpy.ops.render.render(animation=True)
print("CLIP", out, n, "frames")
