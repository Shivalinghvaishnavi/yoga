"""Standing yoga, dance and sequenced stretch routines."""
import math
import importlib
from lib import motion, tri, ease, lerp, stand_feet, arms, REST_ARMS, blend, sequence, REG


@motion("side_stretch", period=6.0, cam="front34")
def side_stretch(t):
    k = tri(t / 6, 0.4)
    return {"torso": (0, -26 * k, 0), "root": (0.03 * k, 0, 0), **stand_feet(0.16, 8),
            "hand_L": ({"rel": (0.02 - 0.05 * k, 0.0, 0.46)}, (0.4, 0, -0.3), (0, 0, 0)),
            "hand_R": ({"rel": (-0.10, -0.03, -0.40)}, (-1, 0.7, 0), (0, 0, 0)), "neck": (0, 0)}


@motion("low_impact_dance", period=4.0, cam="front34")
def low_impact_dance(t):
    s = math.sin(2 * math.pi * t / 4)         # step-touch to each side
    left, right = max(s, 0), max(-s, 0)
    return {"root": (0.16 * s, 0, -0.02 + 0.015 * abs(math.sin(4 * math.pi * t / 4))), "torso": (0, 3 * s, 0),
            "foot_L": ((0.167 + 0.20 * left + 0.0 * right - 0.0, -0.027, 0.07 + 0.05 * (1 if left == 0 and s < -0.2 else 0)), 8, 0),
            "foot_R": ((-0.167 - 0.20 * right, -0.027, 0.07 + 0.05 * (1 if right == 0 and s > 0.2 else 0)), 8, 0),
            "hand_L": ({"rel": (0.22, -0.20, -0.05 + 0.18 * abs(s))}, (0.8, 0.4, -1), (0, 0, 0)),
            "hand_R": ({"rel": (-0.22, -0.20, -0.05 + 0.18 * abs(s))}, (-0.8, 0.4, -1), (0, 0, 0))}


@motion("neck_shoulder", period=14.0, cam="close")
def neck_shoulder(t):
    ph = t % 14
    roll = 0.0
    lift = 0.0
    if ph < 3.5:
        roll = 24 * tri(ph / 3.5, 0.4)
    elif ph < 7:
        roll = -24 * tri((ph - 3.5) / 3.5, 0.4)
    else:
        th = 2 * math.pi * (ph - 7) / 7 * 2
        lift = math.sin(th)
    return {"neck_roll": roll, "clav_L": (14 * lift, 8 * math.cos(2 * math.pi * (ph - 7) / 3.5)),
            "clav_R": (14 * lift, 8 * math.cos(2 * math.pi * (ph - 7) / 3.5)) if ph >= 7 else (0, 0),
            **stand_feet(), **REST_ARMS}


def _mod(name):
    return importlib.import_module(name)


def _rest():
    return importlib.import_module("idle").pose(0.0)


def _reach(t):
    k = tri(t / 8, 0.4)
    return {**stand_feet(0.16, 8), "torso": (-6 * k, 0, 0),
            **arms((0.06, -0.02, 0.45 * k - 0.40 * (1 - k)), (-0.06, -0.02, 0.45 * k - 0.40 * (1 - k)), (0.3, 0, -0.2), (-0.3, 0, -0.2))}


def _side(sign):
    def f(t):
        p = REG["side_stretch"]["pose"](t)
        if sign < 0:
            from rigkit import mirror_pose
            return mirror_pose(p)
        return p
    return f


_fold = lambda t: _mod("forward_fold").pose(t)
_quad = lambda t: _mod("quad_stretch").pose(t)
_circ = lambda t: _mod("hip_circles").pose(t)
_shoulder = lambda t: REG["neck_shoulder"]["pose"](t)


def _register(name, parts):
    rest = _rest()
    fn, total = sequence([(d, f) for d, f in parts], rest)
    REG[name] = dict(name=name, FPS=30, PERIOD=total, CAM="front34", BAND=False, PROPS=None, ANCHORS=None, GROUND=False, pose=fn)


_register("full_stretch", [(8, _reach), (6, _side(1)), (6, _side(-1)), (8, _fold), (14, _shoulder)])
def _quad_r(t):
    from rigkit import mirror_pose
    return mirror_pose(_quad(t))


_register("lower_stretch", [(8, _fold), (6, _quad), (6, _quad_r), (8, _circ)])
