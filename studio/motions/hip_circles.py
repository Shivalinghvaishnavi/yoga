"""Standing hip circles, hands on hips, feet a little wider than hips."""
import math

FPS, PERIOD = 30, 4.0
ANK_L, ANK_R = (0.21, -0.027, 0.07), (-0.21, -0.027, 0.07)


def pose(t):
    th = 2 * math.pi * t / PERIOD
    c, s = math.cos(th), math.sin(th)
    return {
        "root": (0.05 * c, 0.05 * s, -0.02), "root_rot": (4 * s, -4 * c, 0), "torso": (-2 * s, 2 * c, 0),
        "foot_L": (ANK_L, 14, 0), "foot_R": (ANK_R, 14, 0),
        "hand_L": ({"rel": (0.08, -0.03, -0.42)}, (1.0, 0.7, 0), (0, 0, 0)),
        "hand_R": ({"rel": (-0.08, -0.03, -0.42)}, (-1.0, 0.7, 0), (0, 0, 0)),
    }
