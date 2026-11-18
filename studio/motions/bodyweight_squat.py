"""Bodyweight squat, one rep (sit back, chest up, arms forward for balance)."""
import math
from mathutils import Vector as V

FPS, PERIOD = 30, 4.0
HIP_REST = 0.0
ANK_L, ANK_R = (0.167, -0.027, 0.07), (-0.167, -0.027, 0.07)


def lerp(a, b, k):
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def pose(t):
    # 0..1..0 depth: 1.2s down, 0.4s hold, 1.6s up, 0.8s standing rest
    ph = t / PERIOD
    d = 0.5 - 0.5 * math.cos(2 * math.pi * min(ph / 0.8, 1.0)) if ph < 0.8 else 0.0
    d = max(0.0, min(1.0, d))
    return {
        "root": (0, 0.16 * d, -0.30 * d),
        "torso": (28 * d, 0, 0),
        "neck": (-18 * d, 0),
        "foot_L": (ANK_L, 12, 0), "foot_R": (ANK_R, 12, 0),
        "hand_L": ({"rel": lerp((0.14, -0.12, -0.34), (0.11, -0.45, 0.0), d)}, (0.5, 0.3, -1), (0, 0, 0)),
        "hand_R": ({"rel": lerp((-0.14, -0.12, -0.34), (-0.11, -0.45, 0.0), d)}, (-0.5, 0.3, -1), (0, 0, 0)),
    }
