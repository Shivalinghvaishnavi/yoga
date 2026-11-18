"""Standing calf raise: rise onto the balls of the feet, hold, lower slowly. Hands on hips."""
import math

FPS, PERIOD = 30, 4.0
ANK_L, ANK_R = (0.167, -0.027, 0.07), (-0.167, -0.027, 0.07)


def pose(t):
    ph = t / PERIOD
    if ph < 0.25:
        u = 0.5 - 0.5 * math.cos(math.pi * ph / 0.25)
    elif ph < 0.45:
        u = 1.0
    elif ph < 0.85:
        u = 0.5 + 0.5 * math.cos(math.pi * (ph - 0.45) / 0.4)
    else:
        u = 0.0
    def a(c):
        return (c[0], c[1] - 0.045 * u, c[2] + 0.09 * u)
    return {
        "root": (0, -0.03 * u, 0.09 * u),
        "foot_L": (a(ANK_L), 0, 38 * u), "foot_R": (a(ANK_R), 0, 38 * u),
        "hand_L": ({"rel": (0.08, -0.03, -0.42)}, (1.0, 0.7, 0), (0, 0, 0)),
        "hand_R": ({"rel": (-0.08, -0.03, -0.42)}, (-1.0, 0.7, 0), (0, 0, 0)),
    }
