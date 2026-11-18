"""Standing ready pose with gentle breathing. Used for intros, set-ups and rests."""
import math

FPS, PERIOD = 30, 4.0
ANK_L, ANK_R = (0.167, -0.027, 0.07), (-0.167, -0.027, 0.07)


def pose(t):
    b = math.sin(2 * math.pi * t / PERIOD)
    return {
        "torso": (1.2 * b, 0, 0), "neck": (-0.6 * b, 0),
        "foot_L": (ANK_L, 8, 0), "foot_R": (ANK_R, 8, 0),
        "hand_L": ({"rel": (0.14, -0.12, -0.34 + 0.004 * b)}, (0.5, 0.3, -1), (0, 0, 0)),
        "hand_R": ({"rel": (-0.14, -0.12, -0.34 + 0.004 * b)}, (-0.5, 0.3, -1), (0, 0, 0)),
    }
