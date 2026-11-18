"""Resistance-band squat: stand on the band, handles at shoulders, sit back, drive up."""
import math

FPS, PERIOD, BAND = 30, 5.0, True
ANK_L, ANK_R = (0.19, -0.027, 0.07), (-0.19, -0.027, 0.07)


def lerp(a, b, k):
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def pose(t):
    ph = t / PERIOD
    d = 0.5 - 0.5 * math.cos(2 * math.pi * ph / 0.8) if ph < 0.8 else 0.0
    d = max(0.0, min(1.0, d))
    hl, hr = (0.07, -0.19, -0.02), (-0.07, -0.19, -0.02)   # handles held at shoulders
    return {
        "root": (0, 0.15 * d, -0.29 * d), "torso": (24 * d, 0, 0), "neck": (-14 * d, 0),
        "foot_L": (ANK_L, 14, 0), "foot_R": (ANK_R, 14, 0),
        "hand_L": ({"rel": lerp((0.14, -0.12, -0.34), hl, min(1, ph * 12))}, (0.6, 0.3, -1), (0, 0, 0)),
        "hand_R": ({"rel": lerp((-0.14, -0.12, -0.34), hr, min(1, ph * 12))}, (-0.6, 0.3, -1), (0, 0, 0)),
    }
