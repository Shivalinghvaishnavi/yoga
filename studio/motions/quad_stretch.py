"""Standing quad stretch (left foot held behind): settle in, hold with gentle breathing, release. Mirror with __R."""
import math

FPS, PERIOD = 30, 6.0
ANK_L, ANK_R = (0.14, -0.027, 0.07), (-0.14, -0.027, 0.07)


def pose(t):
    ph = t / PERIOD
    k = 0.5 - 0.5 * math.cos(math.pi * min(ph / 0.2, 1)) if ph < 0.8 else 0.5 + 0.5 * math.cos(math.pi * min((ph - 0.8) / 0.2, 1))
    b = 0.15 * math.sin(2 * math.pi * ph * 2)
    return {
        "root": (-0.03 * k, 0.0, 0), "torso": (0, 0, 0),
        "foot_L": ({"rel": (0.0, 0.05 + 0.18 * k, -0.62 + 0.38 * k)}, 0, 0),
        "foot_R": (ANK_R, 8, 0),
        "hand_L": ({"at": "foot.L", "off": (0.0, 0.02, 0.03)} if k > 0.02 else {"rel": (0.14, -0.12, -0.34)}, (0.8, 0.5, -0.6), (0, 0, 0)),
        "hand_R": ({"rel": (-0.40, -0.10, 0.08 + 0.02 * b)}, (-0.3, 0.3, -1), (0, 0, 0)),
    }
