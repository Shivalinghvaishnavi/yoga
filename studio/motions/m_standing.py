"""Standing, band and wall exercises. Axes: +x her left, -y forward, +z up. Rep period = 4 s (one rep)."""
import math
from mathutils import Vector as V
from lib import motion, tri, ease, lerp, wrap, stand_feet, arms, REST_ARMS

wrap("bodyweight_squat", "bw_squat", 4.0, "front34")
wrap("band_squat", "band_squat", 4.0, "front34", band=True)
wrap("glute_bridge", "glute_bridge", 4.0, "floor_side")
wrap("march", "march", 2.0, "front34")
wrap("march", "brisk_walk", 1.6, "front34")
wrap("march", "gentle_walk", 2.6, "front34")
wrap("hip_circles", "hip_circles", 4.0, "front34")
wrap("arm_circles", "arm_circles", 4.0, "front34")


@motion("band_rdl", period=4.0, cam="sideview", band=True)
def band_rdl(t):
    k = tri(t / 4, 0.5)
    return {"root": (0, 0.20 * k, -0.10 * k), "torso": (62 * k, 0, 0), "neck": (-22 * k, 0),
            **stand_feet(0.14, 6), **arms((0.10, -0.04, -0.42), (-0.10, -0.04, -0.42), (0.5, 0.5, -1), (-0.5, 0.5, -1))}


@motion("band_deadlift", period=4.0, cam="sideview", band=True)
def band_deadlift(t):
    k = tri(t / 4, 0.5)
    return {"root": (0, 0.24 * k, -0.24 * k), "torso": (52 * k, 0, 0), "neck": (-20 * k, 0),
            **stand_feet(0.19, 10), **arms((0.12, -0.04, -0.42), (-0.12, -0.04, -0.42), (0.5, 0.5, -1), (-0.5, 0.5, -1))}


def _lunge_props(props, mirror=False):
    props.wall_side(-0.60 if mirror else 0.60)


@motion("reverse_lunge", period=4.0, cam="side34L", props=_lunge_props)
def reverse_lunge(t):
    k = tri(t / 4, 0.45)
    return {"root": (0, 0.16 * k, -0.30 * k), "torso": (4, 0, 0),
            "foot_L": ((0.11, -0.03, 0.07), 6, 0),
            "foot_R": ((-0.11, -0.03 + 0.64 * k, 0.07 + 0.20 * k), 6, -48 * k),
            "hand_L": ({"rel": (0.40, -0.02, -0.10)}, (1, 0.2, -0.3), (0, 0, 0)),
            "hand_R": ({"rel": (-0.08, -0.03, -0.42)}, (-1, 0.7, 0), (0, 0, 0))}


def _chair_props(props, mirror=False):
    props.chair(y=0.24, seat_h=0.46)


@motion("sit_to_stand", period=4.0, cam="side34", props=_chair_props)
def sit_to_stand(t):
    ph = t / 4
    k = ease((ph - 0.08) / 0.34) if ph < 0.5 else ease((0.95 - ph) / 0.30)
    return {"root": (0, lerp((0.106,), (-0.314,), k)[0], -0.28 * (1 - k)), "torso": (5 + 28 * math.sin(math.pi * k), 0, 0),
            "neck": (-6 * math.sin(math.pi * k), 0),
            "foot_L": ((0.14, -0.28, 0.07), 6, 0), "foot_R": ((-0.14, -0.28, 0.07), 6, 0),
            **arms((0.09, -0.40, -0.05), (-0.09, -0.40, -0.05), (0.5, 0, -1), (-0.5, 0, -1))}


@motion("band_curl", period=4.0, cam="front34", band=True)
def band_curl(t):
    k = tri(t / 4, 0.5)
    phi = math.radians(12 + 120 * k)
    def rel(sx):
        return (sx * 0.11, -0.22 * math.sin(phi), -0.24 - 0.22 * math.cos(phi))
    return {**stand_feet(0.15, 8), **arms(rel(1), rel(-1), (0.4, 0.8, -1), (-0.4, 0.8, -1))}


def _tube_between_hands(rig, t):
    return {"floor_L": rig.head("wrist.R"), "floor_R": rig.head("wrist.L")}


@motion("band_pullapart", period=4.0, cam="front34", band=True, anchors=_tube_between_hands)
def band_pullapart(t):
    k = tri(t / 4, 0.5)
    x = 0.10 + 0.20 * k
    return {**stand_feet(0.14, 6), "torso": (0, 0, 0),
            **arms((x, -0.44, -0.02), (-x, -0.44, -0.02), (0.6, 0.2, 1), (-0.6, 0.2, 1))}


def _wall_front(props, mirror=False):
    props.wall(-0.88)


@motion("wall_pushup", period=4.0, cam="sideview", props=_wall_front)
def wall_pushup(t):
    k = tri(t / 4, 0.5)
    a = math.radians(18 + 14 * k)
    py, pz = -0.027 - 0.80 * math.sin(a), 0.07 + 0.79 * math.cos(a)
    return {"root": (0, py - 0.064, pz - 0.861), "root_rot": (math.degrees(a), 0, 0), "neck": (-10, 0),
            "foot_L": ((0.12, -0.027, 0.07), 6, 0), "foot_R": ((-0.12, -0.027, 0.07), 6, 0),
            "hand_L": ((0.24, -0.85, 1.22), (1, 0.3, -0.4), (0, 0, 0)),
            "hand_R": ((-0.24, -0.85, 1.22), (-1, 0.3, -0.4), (0, 0, 0))}


def _wall_back(props, mirror=False):
    props.wall(0.27)


@motion("wall_angels", period=4.0, cam="front34", props=_wall_back)
def wall_angels(t):
    k = tri(t / 4, 0.5)
    l = lerp((0.27, 0.07, 0.20), (0.14, 0.05, 0.43), k)
    return {"root": (0, 0.02, -0.05), "torso": (-2, 0, 0), "neck": (4, 0),
            "foot_L": ((0.12, -0.26, 0.07), 6, 0), "foot_R": ((-0.12, -0.26, 0.07), 6, 0),
            **arms(l, (-l[0], l[1], l[2]), (1, 0.4, -0.6), (-1, 0.4, -0.6))}


@motion("chin_tucks", period=4.0, cam="profile")
def chin_tucks(t):
    k = tri(t / 4, 0.3) if (t / 4) % 1 < 0.7 else 0.0   # tuck, hold, release
    k = ease(min(1, (t / 4) / 0.25)) if t / 4 < 0.7 else ease(max(0, 1 - ((t / 4) - 0.7) / 0.25))
    return {"head_shift": (0, -0.05 + 0.08 * k, 0), "neck": (8 - 14 * k, 0), **stand_feet(), "torso": (0, 0, 0),
            **arms((0.14, -0.12, -0.34), (-0.14, -0.12, -0.34))}


def _doorway(props, mirror=False):
    props.door(x_half=0.43, y=-0.05)


@motion("doorway_chest", period=14.0, cam="front34", props=_doorway)
def doorway_chest(t):
    from rigkit import mirror_pose
    side2 = t >= 7
    tt = t - 7 if side2 else t
    ph = tt / 7
    k = ease(ph / 0.35) if ph < 0.7 else ease((1 - ph) / 0.3)
    p = {"root": (0.0, -0.20 * k, -0.01), "torso": (3, 0, -16 * k), "neck": (0, 0),
         "foot_L": ((0.12, -0.03, 0.07), 6, 0), "foot_R": ((-0.12, -0.03 - 0.52 * k, 0.07), 10, 0),
         "hand_L": ((0.40, -0.10, 1.53), (1, 0.2, -0.4), (0, 0, 0)),
         "hand_R": ({"rel": (-0.08, -0.03, -0.42)}, (-1, 0.7, 0), (0, 0, 0))}
    return mirror_pose(p) if side2 else p


@motion("shoulder_rolls", period=4.0, cam="close")
def shoulder_rolls(t):
    th = 2 * math.pi * t / 4
    return {"clav_L": (30 * math.sin(th), 20 * math.cos(th)), "clav_R": (30 * math.sin(th), 20 * math.cos(th)),
            **stand_feet(), **REST_ARMS}


wrap("side_leg_raise", "side_leg_raise", 4.0, "floor_front")


def _pallof_props(props, mirror=False):
    x = -1.05 if mirror else 1.05
    props.wall_side(x + (0.03 if not mirror else -0.03))
    props.anchor(x - (0.03 if not mirror else -0.03))


def _pallof_anchors(rig, t):
    mid = (rig.head("wrist.L") + rig.head("wrist.R")) * 0.5
    a = V((1.0, 0.0, 1.30))
    return {"handle_L": mid, "handle_R": mid, "floor_L": a, "floor_R": a}


@motion("pallof_press", period=4.0, cam="front34", band=True, props=_pallof_props, anchors=_pallof_anchors)
def pallof_press(t):
    k = tri(t / 4, 0.45)
    return {"root": (-0.02 * k, 0, 0), "torso": (0, 0, 6 * k), **stand_feet(0.15, 8),
            **arms((-0.13, -0.18 - 0.27 * k, -0.14 + 0.04 * k), (0.13, -0.18 - 0.27 * k, -0.14 + 0.04 * k), (0.3, 0.3, -1), (-0.3, 0.3, -1))}
