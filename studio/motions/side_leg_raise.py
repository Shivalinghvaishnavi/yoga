"""Side-lying leg raise: lie on right side, lift the top (left) leg, lower with control."""
import math

FPS, PERIOD = 30, 5.0


def pose(t):
    ph = t / PERIOD
    k = (0.5 - 0.5 * math.cos(2 * math.pi * ph / 0.85)) if ph < 0.85 else 0.0
    return {
        "root": (0, 0, 0.15 - 0.861), "root_rot": (0, -90, 0), "neck": (0, 0),
        "foot_L": ({"rel": (0.0 + 0.15 * k, 0.0, -0.80 - 0.0)}, 0, 0) if False else ({"rel": (0.70, 0.0, 0.12 + 0.33 * k)}, 0, 0),
        "foot_R": ({"rel": (0.45, 0.20, -0.02)}, 0, 0),
        "hand_L": ((0.0, -0.30, 0.45), (0, 0, 1), (0, 0, 0)),
        "hand_R": ((-0.35, -0.05, 0.12), (0, 0, 1), (0, 0, 0)),
    }
