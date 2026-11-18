"""Motion registry and small helpers. Each motion: period (s), pose(t), camera, optional band/props."""
import math
import importlib

REG = {}


def motion(name, period=4.0, cam="front34", band=False, props=None, anchors=None, fps=30, ground=False):
    def deco(fn):
        REG[name] = dict(name=name, FPS=fps, PERIOD=period, CAM=cam, BAND=band, PROPS=props, ANCHORS=anchors, GROUND=ground, pose=fn)
        return fn
    return deco


class M:  # adapter so registry entries look like the older per-file modules
    def __init__(self, d):
        self.__dict__.update(d)
        if d["ANCHORS"]:
            self.band_anchor = d["ANCHORS"]


def _load_all():
    import glob, os
    for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "m_*.py"))):
        importlib.import_module(os.path.basename(f)[:-3])


def load(name):
    base = name[:-3] if name.endswith("__R") else name
    if not REG:
        _load_all()
    if base in REG:
        return M(REG[base])
    return importlib.import_module(base)


def ease(x):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, x)))


def tri(ph, up=0.5):
    """0 -> 1 -> 0 over one period, smooth; `up` = fraction of the period spent rising."""
    ph %= 1.0
    return ease(ph / up) if ph < up else ease((1 - ph) / (1 - up))


def lerp(a, b, k):
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def stand_feet(w=0.167, yaw=8, y=-0.027, z=0.07):
    return {"foot_L": ((w, y, z), yaw, 0), "foot_R": ((-w, y, z), yaw, 0)}


def arms(l, r, pole_l=(0.5, 0.3, -1), pole_r=(-0.5, 0.3, -1)):
    """Both hands as offsets from the shoulders (armature axes: +x her left, -y forward, +z up)."""
    return {"hand_L": ({"rel": l}, pole_l, (0, 0, 0)), "hand_R": ({"rel": r}, pole_r, (0, 0, 0))}


REST_ARMS = arms((0.14, -0.12, -0.34), (-0.14, -0.12, -0.34))


def wrap(old, name, period, cam="front34", band=False, props=None):
    """Register an older per-file motion under a new name, stretched to a new period."""
    m = importlib.import_module(old)
    scale = m.PERIOD / period
    REG[name] = dict(name=name, FPS=m.FPS, PERIOD=period, CAM=cam, BAND=band or getattr(m, "BAND", False), PROPS=props,
                     ANCHORS=getattr(m, "band_anchor", None), GROUND=False, pose=lambda t, m=m, s=scale: m.pose(t * s))


def blend(a, b, k):
    """Interpolate two pose dicts (numbers, tuples and {'rel': ...} targets); keys only in `a` stay as they are."""
    def mix(x, y):
        if isinstance(x, dict):
            return {kk: mix(x[kk], y[kk]) if kk in y else x[kk] for kk in x}
        if isinstance(x, (tuple, list)):
            return tuple(mix(p, q) for p, q in zip(x, y)) if isinstance(y, (tuple, list)) and len(x) == len(y) else x
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            return x + (y - x) * k
        return x
    return {kk: mix(a[kk], b[kk]) if kk in b else a[kk] for kk in a}


def sequence(parts, rest):
    """Play (duration, pose_fn) parts in turn, easing through the `rest` pose for 0.6 s at each join."""
    total = sum(d for d, _ in parts)
    def pose(t):
        t %= total
        for d, fn in parts:
            if t < d:
                edge = min(t, d - t)
                k = ease(edge / 0.6) if edge < 0.6 else 1.0
                return blend(rest, fn(t), k)
            t -= d
    return pose, total
