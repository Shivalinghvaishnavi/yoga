"""Resistance band with two handles. Segments are stretched cylinders between keyed empties."""
import bpy
from mathutils import Vector as V

CORAL = (0.80, 0.22, 0.17)


def _mat(rgb):
    m = bpy.data.materials.new("Band")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = 0.5
    return m


class Band:
    """Anchors: handle_L, handle_R (hands), floor_L, floor_R (under each foot)."""
    NAMES = ["handle_L", "handle_R", "floor_L", "floor_R"]

    def __init__(self, width=0.035, thick=0.006):
        self.mat = _mat(CORAL)
        self.empty = {}
        for n in self.NAMES:
            e = bpy.data.objects.new("band_" + n, None)
            bpy.context.scene.collection.objects.link(e)
            self.empty[n] = e
        for a, b in (("handle_L", "floor_L"), ("handle_R", "floor_R"), ("floor_L", "floor_R")):
            self._segment(a, b, width, thick)
        for n in ("handle_L", "handle_R"):
            self._handle(n)

    def _segment(self, a, b, w, t):
        bpy.ops.mesh.primitive_cube_add(size=1)
        o = bpy.context.object
        o.name = f"band_{a}_{b}"
        o.data.materials.append(self.mat)
        for v in o.data.vertices:          # unit length along +Y, origin at start
            v.co = (v.co.x * w, v.co.y + 0.5, v.co.z * t)
        o.location = (0, 0, 0)
        c = o.constraints.new("STRETCH_TO")
        c.target, c.rest_length, c.volume = self.empty[b], 1.0, "NO_VOLUME"
        c.keep_axis = "PLANE_Z"
        o.parent = self.empty[a]

    def _handle(self, n):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=0.11, rotation=(0, 1.5708, 0))
        o = bpy.context.object
        o.name = "handle_" + n
        m = bpy.data.materials.new("Handle")
        m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.05, 0.06, 1)
        o.data.materials.append(m)
        o.parent = self.empty[n]

    def update(self, rig, frame, anchors=None):
        """Default anchors: handles just beyond each wrist, floor points under the foot arches."""
        pos = {}
        for s, side in (("L", ".L"), ("R", ".R")):
            w, e = rig.head("wrist" + side), rig.head("lowerarm02" + side)
            pos["handle_" + s] = w + (w - e).normalized() * 0.07
            f = rig.head("foot" + side)
            pos["floor_" + s] = V((f.x, f.y - 0.07, 0.016))
        if anchors:
            pos.update(anchors)
        for n, p in pos.items():
            self.empty[n].location = p
            self.empty[n].keyframe_insert("location", frame=frame)
