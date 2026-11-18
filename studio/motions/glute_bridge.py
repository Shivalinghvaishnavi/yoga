"""Glute bridge: lie on back, knees bent, lift hips, squeeze, lower."""
import math

FPS, PERIOD = 30, 5.0
FLOOR = 0.012


def pose(t):
    ph = t / PERIOD
    if ph < 0.3:
        k = 0.5 - 0.5 * math.cos(math.pi * ph / 0.3)
    elif ph < 0.5:
        k = 1.0
    elif ph < 0.85:
        k = 0.5 + 0.5 * math.cos(math.pi * (ph - 0.5) / 0.35)
    else:
        k = 0.0
    a = 20 * k                                    # hip-lift angle about the shoulders
    pelvis_z = 0.15 + 0.5 * math.sin(math.radians(a))
    return {
        "root": (0, 0.0 + 0.5 * (1 - math.cos(math.radians(a))), pelvis_z - 0.861),
        "root_rot": (-90 - a, 0, 0), "neck": (35, 0), "torso": (0, 0, 0),
        "foot_L": ((0.16, -0.30, 0.07), 6, 0), "foot_R": ((-0.16, -0.30, 0.07), 6, 0),
        "hand_L": ((0.22, 0.38, 0.05), (1, 0, 0.5), (0, 0, 0)),
        "hand_R": ((-0.22, 0.38, 0.05), (-1, 0, 0.5), (0, 0, 0)),
    }
