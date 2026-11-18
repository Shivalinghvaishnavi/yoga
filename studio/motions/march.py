"""Marching on the spot: alternate knee lifts with opposite-arm swing (warm-up)."""
import math

FPS, PERIOD = 30, 2.0
A = {"L": (0.167, -0.027, 0.07), "R": (-0.167, -0.027, 0.07)}


def pose(t):
    s = math.sin(2 * math.pi * t / PERIOD)          # +: left knee up, -: right knee up
    up = lambda v: max(0.0, v)
    def foot(side, lift):
        a = A[side]
        return ((a[0], a[1] - 0.14 * lift, a[2] + 0.22 * lift), 6, -10 * lift)
    return {
        "root": (0, 0, 0.012 * abs(math.cos(2 * math.pi * t / PERIOD)) - 0.01),
        "torso": (0, 0, 5 * s),
        "foot_L": foot("L", up(s)), "foot_R": foot("R", up(-s)),
        "hand_L": ({"rel": (0.12, -0.18 + 0.20 * -s, -0.30)}, (0.6, 0.2, -1), (0, 0, 0)),
        "hand_R": ({"rel": (-0.12, -0.18 + 0.20 * s, -0.30)}, (-0.6, 0.2, -1), (0, 0, 0)),
    }
