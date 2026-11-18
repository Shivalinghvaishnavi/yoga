"""Pose solver for the MPFB2 'default' rig: analytic 2-bone IK for legs/arms + FK spine.

All maths is in armature space (= world; rig sits at the origin, faces -Y, her left is +X).
A pose is a plain dict (see `solve`), so exercises are just functions time -> pose.
"""
import math
import bpy
from mathutils import Matrix, Vector as V

LIMBS = {  # side -> (upper, lower, end) bones
    "leg": ("upperleg01", "lowerleg01", "foot"),
    "arm": ("upperarm01", "lowerarm01", "wrist"),
}
SPINE = ["spine05", "spine04", "spine03", "spine02", "spine01"]
NECK = ["neck01", "neck02", "neck03", "head"]


def rx(deg): return Matrix.Rotation(math.radians(deg), 3, "X")
def ry(deg): return Matrix.Rotation(math.radians(deg), 3, "Y")
def rz(deg): return Matrix.Rotation(math.radians(deg), 3, "Z")


class Rig:
    def __init__(self, arm):
        self.arm, self.pb = arm, arm.pose.bones
        for p in self.pb:
            p.rotation_mode = "QUATERNION"
        self.rest = {b.name: b.head_local.copy() for b in arm.data.bones}
        self.rest_rot = {b.name: b.matrix_local.to_3x3() for b in arm.data.bones}

    # -- primitives --------------------------------------------------------
    @staticmethod
    def update():
        bpy.context.view_layer.update()

    def reset(self):
        for p in self.pb:
            p.location, p.rotation_quaternion, p.scale = (0, 0, 0), (1, 0, 0, 0), (1, 1, 1)
        self.update()

    def head(self, name): return self.pb[name].head.copy()

    def rotate_about(self, name, pivot, R3):
        T = Matrix.Translation
        self.pb[name].matrix = T(pivot) @ R3.to_4x4() @ T(-pivot) @ self.pb[name].matrix
        self.update()

    def translate(self, name, v):
        self.pb[name].matrix = Matrix.Translation(v) @ self.pb[name].matrix
        self.update()

    def aim(self, name, pivot, cur, want):
        self.rotate_about(name, pivot, (cur - pivot).rotation_difference(want - pivot).to_matrix())

    # -- limbs -------------------------------------------------------------
    def ik2(self, kind, side, target, pole):
        up, lo, en = (n + side for n in LIMBS[kind])
        H, Kc, Ac = self.head(up), self.head(lo), self.head(en)
        L1, L2 = (Kc - H).length, (Ac - Kc).length
        d = target - H
        dist = min(max(d.length, abs(L1 - L2) + 1e-4), L1 + L2 - 1e-4)
        u = d.normalized()
        a = (L1 ** 2 - L2 ** 2 + dist ** 2) / (2 * dist)
        h = math.sqrt(max(L1 ** 2 - a ** 2, 0.0))
        pv = (pole - u * pole.dot(u)).normalized()
        K, A = H + u * a + pv * h, H + u * dist
        self.aim(up, H, Kc, K)
        self.aim(lo, K, self.head(en), A)
        return A

    def foot(self, side, target, yaw=0.0, pitch=0.0, toe_out_sign=1, pole=(0, -1, 0)):
        A = self.ik2("leg", side, target, V(pole))
        name = "foot" + side
        R = rz(yaw * toe_out_sign) @ rx(pitch) @ self.rest_rot[name]
        self.pb[name].matrix = Matrix.Translation(A) @ R.to_4x4()
        self.update()

    def hand(self, side, target, pole, rot=(0, 0, 0)):
        A = self.ik2("arm", side, target, pole)
        if any(rot):
            self.rotate_about("wrist" + side, A, rz(rot[2]) @ ry(rot[1]) @ rx(rot[0]))

    # -- spine / head ------------------------------------------------------
    def torso(self, flex=0.0, side=0.0, twist=0.0):
        n = len(SPINE)
        for s in SPINE:
            self.rotate_about(s, self.head(s), rz(twist / n) @ ry(side / n) @ rx(flex / n))

    def neck(self, pitch=0.0, yaw=0.0):
        for s in NECK:
            self.rotate_about(s, self.head(s), rz(yaw / 4) @ rx(pitch / 4))

    # -- whole body --------------------------------------------------------
    def solve(self, p):
        """p keys: root=(dx,dy,dz), root_rot=(pitch,roll,yaw), torso=(flex,side,twist), neck=(pitch,yaw),
        foot_L/foot_R=(target xyz, yaw, pitch), hand_L/hand_R=(target xyz, pole xyz, rot xyz)."""
        self.reset()
        dx, dy, dz = p.get("root", (0, 0, 0))
        self.translate("root", V((dx, dy, dz)))
        rp, rr, ry_ = p.get("root_rot", (0, 0, 0))
        if rp or rr or ry_:
            self.rotate_about("root", self.head("root"), rz(ry_) @ ry(rr) @ rx(rp))
        f, s, t = p.get("torso", (0, 0, 0))
        if f or s or t:
            self.torso(f, s, t)
        npitch, nyaw = p.get("neck", (0, 0))
        if npitch or nyaw:
            self.neck(npitch, nyaw)
        hs = p.get("head_shift")
        if hs:
            self.translate("neck03", V(hs) * 0.5)
            self.translate("head", V(hs))
        nroll = p.get("neck_roll", 0)
        if nroll:
            for sname in NECK:
                self.rotate_about(sname, self.head(sname), ry(nroll / 4))
        for side, key in ((".L", "clav_L"), (".R", "clav_R")):   # (lift deg, forward deg)
            if key in p:
                lift, fwd = p[key]
                sgn = 1 if side == ".L" else -1
                self.rotate_about("clavicle" + side, self.head("clavicle" + side), ry(sgn * lift) @ rz(sgn * -fwd))
        for side, key in ((".L", "foot_L"), (".R", "foot_R")):
            tgt, yaw, pitch, *rest = p[key]
            tgt = self.head("upperleg01" + side) + V(tgt["rel"]) if isinstance(tgt, dict) else V(tgt)
            self.foot(side, tgt, yaw, pitch, 1 if side == ".L" else -1, rest[0] if rest else (0, -1, 0))
        for side, key in ((".L", "hand_L"), (".R", "hand_R")):
            if key in p:
                tgt, pole, rot = p[key]
                if isinstance(tgt, dict) and "at" in tgt:
                    tgt = self.head(tgt["at"]) + V(tgt.get("off", (0, 0, 0)))
                else:
                    tgt = self.head("upperarm01" + side) + V(tgt["rel"]) if isinstance(tgt, dict) else V(tgt)
                self.hand(side, tgt, V(pole), rot)


def _mx(v):
    return (-v[0], v[1], v[2])


def mirror_pose(p):
    """Left/right mirror of a pose dict (swap sides, negate x, roll/yaw)."""
    q = {}
    for k, v in p.items():
        if k == "root":
            q[k] = _mx(v)
        elif k == "root_rot":
            q[k] = (v[0], -v[1], -v[2])
        elif k == "torso":
            q[k] = (v[0], -v[1], -v[2])
        elif k == "neck":
            q[k] = (v[0], -v[1])
        elif k == "head_shift":
            q[k] = _mx(v)
        elif k == "neck_roll":
            q[k] = -v
        elif k in ("clav_L", "clav_R"):
            q["clav_R" if k == "clav_L" else "clav_L"] = v
        else:
            side = {"foot_L": "foot_R", "foot_R": "foot_L", "hand_L": "hand_R", "hand_R": "hand_L"}[k]
            if k.startswith("foot"):
                tgt, yaw, pitch, *rest = v
                q[side] = (_mt(tgt), yaw, pitch, *( [_mx(rest[0])] if rest else [] ))
            else:
                tgt, pole, rot = v
                q[side] = (_mt(tgt), _mx(pole), (rot[0], -rot[1], -rot[2]))
    return q


def _mt(t):
    if isinstance(t, dict):
        d = dict(t)
        if "rel" in d:
            d["rel"] = _mx(d["rel"])
        if "at" in d:
            d["at"] = d["at"][:-1] + ("R" if d["at"].endswith("L") else "L")
            d["off"] = _mx(d.get("off", (0, 0, 0)))
        return d
    return _mx(t)


def ground(rig, floor=0.012):
    """Shift the whole body vertically so its lowest vertex rests on the mat (used for floor poses)."""
    import numpy as np
    dg = bpy.context.evaluated_depsgraph_get()
    lo = 1e9
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.modifiers or o.hide_render:
            continue
        if not any(m.type == "ARMATURE" for m in o.modifiers):
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        co = np.empty(len(me.vertices) * 3, dtype=np.float32)
        me.vertices.foreach_get("co", co)
        lo = min(lo, float(co.reshape(-1, 3)[:, 2].min()))
        ev.to_mesh_clear()
    if lo < 1e8:
        rig.translate("root", V((0, 0, floor - lo)))
    return lo
