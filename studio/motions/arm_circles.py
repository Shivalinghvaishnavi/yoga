"""Arm circles: arms out to the sides at shoulder height, small controlled circles."""
import math

FPS, PERIOD = 30, 3.0
ANK_L, ANK_R = (0.167, -0.027, 0.07), (-0.167, -0.027, 0.07)


def pose(t):
    th = 2 * math.pi * t / PERIOD
    c, s = math.cos(th), math.sin(th)
    return {
        "torso": (0, 0, 0), "foot_L": (ANK_L, 8, 0), "foot_R": (ANK_R, 8, 0),
        "hand_L": ({"rel": (0.50, -0.02 + 0.13 * c, 0.02 + 0.13 * s)}, (0, 0.3, -1), (0, 0, 0)),
        "hand_R": ({"rel": (-0.50, -0.02 + 0.13 * c, 0.02 + 0.13 * s)}, (0, 0.3, -1), (0, 0, 0)),
    }
