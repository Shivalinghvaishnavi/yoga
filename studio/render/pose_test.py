"""Deformation sanity check: deep squat-ish pose + raised arms. Run like turnaround.py."""
import math, sys, bpy
rig = bpy.data.objects["Human.rig"]
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="POSE")
def rot(name, x=0, y=0, z=0):
    pb = rig.pose.bones[name]; pb.rotation_mode = "XYZ"
    pb.rotation_euler = (math.radians(x), math.radians(y), math.radians(z))
for s in ("L", "R"):
    rot(f"upperleg01.{s}", -70); rot(f"lowerleg01.{s}", 100); rot(f"foot.{s}", -30)
    rot(f"upperarm01.{s}", 0, 0, 0)
rot("upperarm01.L", -80, 0, 0); rot("upperarm01.R", -80, 0, 0)
rot("lowerarm01.L", -20); rot("lowerarm01.R", -20)
rot("spine03", 15)
bpy.ops.object.mode_set(mode="OBJECT")
exec(open("/Users/vaishnavi/development/Latest/yogaflow/studio/render/turnaround.py").read())
