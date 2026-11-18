"""Standing forward fold (hamstring stretch) with soft knees: fold, hang, roll up."""
import math

FPS, PERIOD = 30, 8.0
ANK_L, ANK_R = (0.167, -0.027, 0.07), (-0.167, -0.027, 0.07)


def pose(t):
    ph = t / PERIOD
    k = 0.5 - 0.5 * math.cos(math.pi * min(ph / 0.25, 1)) if ph < 0.75 else 0.5 + 0.5 * math.cos(math.pi * min((ph - 0.75) / 0.25, 1))
    return {
        "root": (0, 0.14 * k, -0.03 * k), "torso": (80 * k, 0, 0), "neck": (30 * k, 0),
        "foot_L": (ANK_L, 8, 0), "foot_R": (ANK_R, 8, 0),
        "hand_L": ({"rel": (0.13 * k + 0.14 * (1 - k), -0.02 * k - 0.12 * (1 - k), -0.5 * k - 0.34 * (1 - k))}, (0.5, 0.3, -1), (0, 0, 0)),
        "hand_R": ({"rel": (-0.13 * k - 0.14 * (1 - k), -0.02 * k - 0.12 * (1 - k), -0.5 * k - 0.34 * (1 - k))}, (-0.5, 0.3, -1), (0, 0, 0)),
    }
