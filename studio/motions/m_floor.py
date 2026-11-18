"""Floor and yoga exercises. Lying: root_rot pitch -90 (face up, head toward +y). All fours / child's pose: pitch +90
(face down, head toward -y). For a horizontal torso, 'flex' bends it up/down, 'side' twists about the body axis."""
import math
from mathutils import Vector as V
from lib import motion, tri, ease, lerp, stand_feet, arms, REST_ARMS

UP = (0, 0, 1)


def _supine(pz=0.15, **extra):
    d = {"root": (0, 0, pz - 0.861), "root_rot": (-90, 0, 0), "neck": (30, 0)}
    d.update(extra)
    return d


@motion("dead_bug", period=8.0, cam="floor34", ground=True)
def dead_bug(t):
    ph = (t / 8) % 1
    s = ease(ph / 0.25) if ph < 0.5 else ease((1 - ph) / 0.25)   # 0 -> 1 (left arm/right leg) ... back
    s = min(1.0, s)
    a = 0 if ph < 0.5 else 1
    k = tri((ph % 0.5) / 0.5, 0.5)
    def leg(x, ext):
        return ((x, -0.39 + (-0.38) * ext, 0.54 - 0.32 * ext), 0, 0, (0, 0.5 + 0.0 * ext, 1 - 0.9 * ext))
    def arm(x, ext):
        return ((x, 0.50 + 0.46 * ext, 0.62 - 0.52 * ext), (x * 4, 0, 1), (0, 0, 0))
    return _supine(0.16, foot_L=leg(0.10, k if a == 1 else 0), foot_R=leg(-0.10, k if a == 0 else 0),
                   hand_L=arm(0.17, k if a == 0 else 0), hand_R=arm(-0.17, k if a == 1 else 0))


def _allfours(pelvis_y=0.0, pz=0.52):
    sy = pelvis_y - 0.45
    return {"root": (0, pelvis_y - 0.064, pz - 0.861), "root_rot": (90, 0, 0),
            "foot_L": ((0.10, pelvis_y + 0.39, 0.075), 0, 0, (0, -0.6, -0.8)),
            "foot_R": ((-0.10, pelvis_y + 0.39, 0.075), 0, 0, (0, -0.6, -0.8)),
            "hand_L": ((0.16, sy, 0.06), (0.5, 0.3, 1), (0, 0, 0)),
            "hand_R": ((-0.16, sy, 0.06), (-0.5, 0.3, 1), (0, 0, 0))}


@motion("cat_cow", period=6.0, cam="floor34", ground=True)
def cat_cow(t):
    k = math.sin(2 * math.pi * t / 6)        # +1 cow (belly drops, chest lifts), -1 cat (rounded)
    p = _allfours()
    p.update({"torso": (-16 * k, 0, 0), "neck": (-14 * k, 0)})
    return p


@motion("bird_dog", period=4.0, cam="floor34", ground=True)
def bird_dog(t):
    k = tri(t / 4, 0.4)
    p = _allfours()
    p.update({"torso": (0, 0, 0), "neck": (-10, 0),
              "hand_R": ((-0.14, -0.45 - 0.46 * k, 0.06 + 0.46 * k), (-0.5, 0.3, 1), (0, 0, 0)),
              "foot_L": ((0.10, 0.39 + 0.40 * k, 0.075 + 0.43 * k), 0, -20 * k, (0, -0.6, -0.8))})
    return p


@motion("childs_pose", period=8.0, cam="floor34", ground=True)
def childs_pose(t):
    b = math.sin(2 * math.pi * t / 8)
    return {"root": (0, 0.30 - 0.064, 0.17 - 0.861 + 0.004 * b), "root_rot": (82, 0, 0), "neck": (20, 0),
            "foot_L": ((0.10, 0.33, 0.075), 0, 0, (0, -1, -0.3)), "foot_R": ((-0.10, 0.33, 0.075), 0, 0, (0, -1, -0.3)),
            "hand_L": ((0.16, -0.62, 0.06), (0.5, 0.3, 1), (0, 0, 0)), "hand_R": ((-0.16, -0.62, 0.06), (-0.5, 0.3, 1), (0, 0, 0))}


@motion("thread_needle", period=8.0, cam="floor34", ground=True)
def thread_needle(t):
    k = tri(t / 8, 0.4)
    p = _allfours()
    p.update({"torso": (0, 30 * k, 0), "neck": (-6, 30 * k),
              "hand_R": ((-0.16 + 0.38 * k, -0.45 + 0.05 * k, 0.06 + 0.0 * k), (-0.5, 0.3, 1), (0, 0, 0))})
    return p


@motion("seated_fold", period=8.0, cam="floor_side", ground=True)
def seated_fold(t):
    k = tri(t / 8, 0.45)
    return {"root": (0, 0.30 - 0.064, 0.10 - 0.861), "torso": (62 * k, 0, 0), "neck": (20 * k, 0),
            "foot_L": ((0.10, -0.47, 0.10), 0, 0, (0, 0, 1)), "foot_R": ((-0.10, -0.47, 0.10), 0, 0, (0, 0, 1)),
            "hand_L": ((0.12, -0.28 - 0.14 * k, 0.12), (0.5, 0.3, 1), (0, 0, 0)),
            "hand_R": ((-0.12, -0.28 - 0.14 * k, 0.12), (-0.5, 0.3, 1), (0, 0, 0))}


@motion("butterfly", period=8.0, cam="floor34", ground=True)
def butterfly(t):
    k = tri(t / 8, 0.4)
    return {"root": (0, 0.10 - 0.064, 0.10 - 0.861), "torso": (6 + 22 * k, 0, 0), "neck": (8 * k, 0),
            "foot_L": ((0.04, -0.30, 0.08), 0, 0, (1, -0.2, 0.2)), "foot_R": ((-0.04, -0.30, 0.08), 0, 0, (-1, -0.2, 0.2)),
            "hand_L": ((0.06, -0.30, 0.12), (0.5, 0.3, 1), (0, 0, 0)), "hand_R": ((-0.06, -0.30, 0.12), (-0.5, 0.3, 1), (0, 0, 0))}


@motion("low_lunge", period=8.0, cam="sideview", ground=True)
def low_lunge(t):
    k = tri(t / 8, 0.4)
    return {"root": (0, -0.12 * k - 0.064, 0.45 - 0.861), "torso": (-4 * k, 0, 0), "neck": (-4, 0),
            "foot_R": ((-0.10, -0.40, 0.07), 6, 0, (0, -1, 0)),
            "foot_L": ((0.10, 0.40 + 0.12 * k, 0.075), 0, -70, (0, -0.3, -1)),
            "hand_R": ((-0.12, -0.34 - 0.10 * k, 0.56), (-0.5, 0.3, 1), (0, 0, 0)),
            "hand_L": ((0.12, -0.34 - 0.10 * k, 0.56), (0.5, 0.3, 1), (0, 0, 0))}


def _lying_knees_up(p0=None, **extra):
    d = _supine(0.15, foot_L=((0.14, -0.32, 0.07), 6, 0, (0, 0.6, 1)), foot_R=((-0.14, -0.32, 0.07), 6, 0, (0, 0.6, 1)))
    d.update(extra)
    return d


@motion("diaphragm_breath", period=6.0, cam="floor34", ground=True)
def diaphragm_breath(t):
    b = 0.5 - 0.5 * math.cos(2 * math.pi * t / 6)
    return _lying_knees_up(root=(0, 0, 0.15 - 0.861 + 0.006 * b), torso=(0, 0, 0),
                           hand_L=((0.07, 0.20, 0.27 + 0.02 * b), (0.5, 0, 1), (0, 0, 0)),
                           hand_R=((-0.07, 0.20, 0.27 + 0.02 * b), (-0.5, 0, 1), (0, 0, 0)))


@motion("body_scan", period=8.0, cam="floor34", ground=True)
def body_scan(t):
    b = 0.5 - 0.5 * math.cos(2 * math.pi * t / 8)
    return _supine(0.15, root=(0, 0, 0.15 - 0.861 + 0.004 * b), neck=(28, 0),
                   foot_L=((0.14, -0.78, 0.12), 12, 0, (0, 0, 1)), foot_R=((-0.14, -0.78, 0.12), 12, 0, (0, 0, 1)),
                   hand_L=((0.30, 0.34, 0.05), (1, 0, 0.5), (0, 0, 0)), hand_R=((-0.30, 0.34, 0.05), (-1, 0, 0.5), (0, 0, 0)))


@motion("supine_twist", period=8.0, cam="floor34", ground=True)
def supine_twist(t):
    k = tri(t / 8, 0.4)
    return _supine(0.15, root_rot=(-90, 50 * k, 0), torso=(0, -46 * k, 0), neck=(30, 0),
                   foot_L=((0.30 * k + 0.12, -0.34, 0.07 + 0.05 * k), 0, 0, (1, 0.2, 0.8)),
                   foot_R=((0.30 * k - 0.12 + 0.12 * k, -0.34, 0.07 + 0.05 * k), 0, 0, (1, 0.2, 0.8)),
                   hand_L=((0.58, 0.50, 0.05), (1, 0, 0.5), (0, 0, 0)), hand_R=((-0.58, 0.50, 0.05), (-1, 0, 0.5), (0, 0, 0)))


@motion("hip_mobility", period=6.0, cam="floor34", ground=True)
def hip_mobility(t):
    s = math.sin(2 * math.pi * t / 6)
    return _supine(0.15, foot_L=((0.34 + 0.12 * s, -0.36, 0.07), 6, 0, (s, 0.4, 1)),
                   foot_R=((-0.34 + 0.12 * s, -0.36, 0.07), 6, 0, (s, 0.4, 1)),
                   hand_L=((0.30, 0.34, 0.05), (1, 0, 0.5), (0, 0, 0)), hand_R=((-0.30, 0.34, 0.05), (-1, 0, 0.5), (0, 0, 0)))


def _towel(props, mirror=False):
    props.towel(y=0.50, z=0.05)


@motion("thoracic_ext_towel", period=6.0, cam="floor_side", ground=True, props=_towel)
def thoracic_ext_towel(t):
    k = tri(t / 6, 0.45)
    return _supine(0.15, torso=(-22 * k, 0, 0), neck=(30 - 18 * k, 0),
                   foot_L=((0.14, -0.30, 0.07), 6, 0, (0, 0.6, 1)), foot_R=((-0.14, -0.30, 0.07), 6, 0, (0, 0.6, 1)),
                   hand_L=({"at": "head", "off": (0.12, 0.08, -0.04)}, (1, 0, 0.3), (0, 0, 0)),
                   hand_R=({"at": "head", "off": (-0.12, 0.08, -0.04)}, (-1, 0, 0.3), (0, 0, 0)))


@motion("thoracic_rotation", period=6.0, cam="floor_front", ground=True)
def thoracic_rotation(t):
    k = tri(t / 6, 0.45)
    return {"root": (0, 0, 0.15 - 0.861), "root_rot": (0, -90, 0), "neck": (0, 0), "torso": (-60 * k, 0, 0),
            "foot_L": ({"rel": (0.40, -0.32, -0.02)}, 0, 0, (0, -1, 0.4)), "foot_R": ({"rel": (0.40, -0.30, -0.04)}, 0, 0, (0, -1, 0.4)),
            "hand_R": ((-0.52, -0.42, 0.14), (0, -1, 0.5), (0, 0, 0)),
            "hand_L": ({"rel": lerp((-0.05, -0.42, 0.0), (-0.05, 0.12, 0.44), k)}, (0, -0.3, 1), (0, 0, 0))}


def _feet_anchors(rig, t):
    """Band loops around the soles of both feet."""
    return {"floor_L": rig.head("foot.L") + V((0, -0.11, 0.02)), "floor_R": rig.head("foot.R") + V((0, -0.11, 0.02))}


@motion("band_row", period=4.0, cam="floor_side", ground=True, band=True, anchors=_feet_anchors)
def band_row(t):
    k = tri(t / 4, 0.5)
    return {"root": (0, 0.30 - 0.064, 0.10 - 0.861), "torso": (-8 * k, 0, 0), "neck": (0, 0),
            "foot_L": ((0.10, -0.46, 0.10), 0, 8, (0, 0, 1)), "foot_R": ((-0.10, -0.46, 0.10), 0, 8, (0, 0, 1)),
            "hand_L": ((0.12, -0.46 + 0.40 * k, 0.40 - 0.05 * k), (1, 0.6, -0.3), (0, 0, 0)),
            "hand_R": ((-0.12, -0.46 + 0.40 * k, 0.40 - 0.05 * k), (-1, 0.6, -0.3), (0, 0, 0))}
