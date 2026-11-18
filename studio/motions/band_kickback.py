"""Band glute kickback (left leg working, then right): hinge slightly, extend leg back, squeeze, return."""
import math

FPS, PERIOD, BAND = 30, 5.0, True
ANK = {"L": (0.14, -0.027, 0.07), "R": (-0.14, -0.027, 0.07)}


def ease(ph):
    return 0.5 - 0.5 * math.cos(2 * math.pi * min(ph, 1.0)) if ph < 1 else 0.0


def pose(t):
    ph = t / PERIOD
    k = ease(ph / 0.8) if ph < 0.8 else 0.0     # working-leg extension 0..1..0
    ank_l = (ANK["L"][0], ANK["L"][1] + 0.38 * k, 0.07 + 0.24 * k)
    return {
        "root": (0, 0.02, -0.04), "torso": (22, 0, 0), "neck": (-14, 0),
        "foot_L": (ank_l, 0, 25 * k), "foot_R": (ANK["R"], 8, 0),
        "hand_L": ({"rel": (0.08, -0.3, -0.18)}, (0.6, 0.3, -1), (0, 0, 0)),
        "hand_R": ({"rel": (-0.08, -0.3, -0.18)}, (-0.6, 0.3, -1), (0, 0, 0)),
    }
