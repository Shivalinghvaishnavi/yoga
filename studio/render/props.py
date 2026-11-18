"""Simple set pieces for exercises: chair, wall, door frame, rolled towel."""
import bpy

_cache = {}


def _mat(name, rgb, rough=0.8):
    if name not in _cache:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*rgb, 1)
        b.inputs["Roughness"].default_value = rough
        _cache[name] = m
    return _cache[name]


def _box(name, size, loc, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name, o.scale = name, size
    o.data.materials.append(mat)
    return o


def chair(y=0.12, seat_h=0.46):
    wood = _mat("ChairWood", (0.55, 0.40, 0.27))
    _box("seat", (0.44, 0.42, 0.04), (0, y, seat_h), wood)
    _box("back", (0.44, 0.04, 0.42), (0, y + 0.20, seat_h + 0.23), wood)
    for sx in (-0.19, 0.19):
        for sy in (-0.17, 0.17):
            _box("leg", (0.04, 0.04, seat_h), (sx, y + sy, seat_h / 2), wood)


def wall(y, z=1.25):
    _box("wall", (4.0, 0.06, 2.5), (0, y, z), _mat("Wall", (0.88, 0.87, 0.84), 0.9))


def door(x_half=0.46, y=-0.05):
    frame = _mat("Frame", (0.93, 0.93, 0.92), 0.6)
    for sx in (-1, 1):
        _box("jamb", (0.09, 0.14, 2.1), (sx * (x_half + 0.045), y, 1.05), frame)
    _box("head", (2 * x_half + 0.18, 0.14, 0.09), (0, y, 2.1), frame)


def towel(y, z=0.06, length=0.5):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=length, rotation=(0, 1.5708, 0), location=(0, y, z))
    o = bpy.context.object
    o.name = "towel"
    o.data.materials.append(_mat("Towel", (0.93, 0.86, 0.62), 0.95))


def wall_side(x):
    """Wall to one side (x>0 her left); hands rest on its inner face."""
    _box("sidewall", (0.06, 4.0, 2.5), (x, 0, 1.25), _mat("Wall", (0.88, 0.87, 0.84), 0.9))


def anchor(x, y=0.0, z=1.30):
    """Door-anchor plate on a side wall at chest height."""
    _box("anchorplate", (0.03, 0.14, 0.20), (x, y, z), _mat("Anchor", (0.10, 0.10, 0.12), 0.5))
