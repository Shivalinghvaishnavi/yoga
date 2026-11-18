"""Build the YogaFlow instructor on an MPFB2 (MakeHuman) base and save instructor_mpfb.blend.

Run:  blender -b --python studio/character/mpfb_build.py
Needs the MPFB2 extension + MakeHuman system assets (CC0) installed in Blender 5.3.
Outfit = casual-suit shirt (teal) + sport-suit leggings (charcoal) + sneakers, wristbands teal L / coral R.
"""
import os
import sys
import bmesh
import bpy
import addon_utils
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
addon_utils.enable("bl_ext.user_default.mpfb", default_set=False)
from bl_ext.user_default.mpfb.services.humanservice import HumanService  # noqa: E402
import common  # noqa: E402

TEAL, CORAL = (0.01, 0.24, 0.27, 1), (0.80, 0.22, 0.17, 1)
SKIN_TINT, HAIR_TINT = (0.80, 0.55, 0.42, 1), (0.30, 0.24, 0.22, 1)


def tint(mat, rgba):
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    links = [l for l in nt.links if l.to_socket == bsdf.inputs["Base Color"]]
    if not links:
        return
    src = links[0].from_socket
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
    mix.inputs[0].default_value = 1.0
    nt.links.new(src, mix.inputs[6])
    mix.inputs[7].default_value = rgba
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])


def solid(mat, rgba, rough=None):
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    for l in [l for l in nt.links if l.to_socket == bsdf.inputs["Base Color"]]:
        nt.links.remove(l)
    bsdf.inputs["Base Color"].default_value = rgba
    if rough is not None:
        bsdf.inputs["Roughness"].default_value = rough


def keep_island(ob, which):
    """Keep only the upper ('top') or lower ('bottom') connected island of a suit mesh."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    seen, islands = set(), []
    for f in bm.faces:
        if f in seen:
            continue
        stack, comp = [f], []
        seen.add(f)
        while stack:
            c = stack.pop()
            comp.append(c)
            for e in c.edges:
                for n in e.link_faces:
                    if n not in seen:
                        seen.add(n)
                        stack.append(n)
        islands.append((sum(v.co.z for c in comp for v in c.verts) / (3 * len(comp)), comp))
    islands.sort(key=lambda t: t[0])
    drop = islands[:-1] if which == "top" else islands[1:]
    bmesh.ops.delete(bm, geom=[f for _, comp in drop for f in comp], context="FACES")
    bm.to_mesh(ob.data)
    bm.free()


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    info = HumanService._create_default_human_info_dict()
    info["phenotype"].update({"gender": 0.0, "age": 0.5, "muscle": 0.55, "weight": 0.45,
                              "proportions": 0.6, "height": 0.55, "cupsize": 0.45, "firmness": 0.6})
    info.update({"rig": "default", "eyes": "high-poly.mhclo", "eyes_material_type": "MAKESKIN",
                 "eyebrows": "eyebrow001.mhclo", "eyelashes": "eyelashes01.mhclo", "hair": "ponytail01.mhclo",
                 "teeth": "teeth_base.mhclo", "skin_mhmat": "young_asian_female.mhmat",
                 "skin_material_type": "MAKESKIN", "clothes_material_type": "MAKESKIN",
                 "clothes": ["female_casualsuit01.mhclo", "female_sportsuit01.mhclo", "shoes05.mhclo"],
                 "alternative_materials": {"2c12f43b-1303-432c-b7ce-d78346baf2e6": "brown.mhmat"}})
    st = HumanService.get_default_deserialization_settings()
    body = HumanService.deserialize_from_dict(info, st)
    rig = bpy.data.objects["Human.rig"]
    obj = {o.name.split(".", 1)[-1]: o for o in bpy.data.objects if o.name.startswith("Human.")}
    obj["Human"] = body

    keep_island(obj["female_casualsuit01"], "top")
    keep_island(obj["female_sportsuit01"], "bottom")
    solid(obj["female_casualsuit01"].active_material, TEAL, 0.65)
    solid(obj["female_sportsuit01"].active_material, (0.04, 0.045, 0.055, 1), 0.7)
    tint(body.active_material, SKIN_TINT)
    tint(obj["ponytail01"].active_material, HAIR_TINT)

    # shirt: lift off the leggings to stop z-fighting at the hem
    sh = obj["female_casualsuit01"]
    sh.data.update()
    for v in sh.data.vertices:
        v.co += v.normal * 0.004

    # shoes: low-cut (drop sock tube above the ankle) + side-matched accents
    bm = bmesh.new()
    bm.from_mesh(obj["shoes05"].data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(v.co.z > 0.10 for v in f.verts)], context="FACES")
    bm.to_mesh(obj["shoes05"].data)
    bm.free()

    # wristbands (teal LEFT, coral RIGHT) rigidly bound to the lower forearm bone
    mats = {"teal": common.make_material("BandTeal", TEAL[:3], 0.6), "coral": common.make_material("BandCoral", CORAL[:3], 0.6)}
    coll = bpy.data.collections.new("Accessories")
    bpy.context.scene.collection.children.link(coll)
    for sf, key in ((".L", "teal"), (".R", "coral")):
        wr = rig.matrix_world @ rig.data.bones["wrist" + sf].head_local
        el = rig.matrix_world @ rig.data.bones["lowerarm01" + sf].head_local
        d = (wr - el).normalized()
        c = wr - d * 0.05
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=0.036, radius2=0.036, depth=0.055)
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.004, segments=2, affect="EDGES")
        rq = Vector((0, 0, 1)).rotation_difference(d)
        for v in bm.verts:
            v.co = c + rq @ v.co
        band = common.finish("Wristband" + sf, bm, mats[key], coll)
        common.bind_rigid(band, rig, "lowerarm02" + sf)

    shoe = obj["shoes05"]
    for s_, sf, key in ((1, ".L", "teal"), (-1, ".R", "coral")):
        vs = [v.co for v in shoe.data.vertices if v.co.x * s_ > 0.02]
        xc = sum(v.x for v in vs) / len(vs)
        ymax, ymin = max(v.y for v in vs), min(v.y for v in vs)
        xlat = max(v.x * s_ for v in vs) * s_
        parts = [
            common.ellipsoid("HeelTab" + sf, (xc, ymax - 0.002, 0.065), (0.010, 0.005, 0.016), mats[key], coll, segs=12, rings=8),
        ]
        for pt in parts:
            common.bind_rigid(pt, rig, "foot" + sf)

    out = os.path.join(HERE, "instructor_mpfb.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    print("SAVED", out, "HEIGHT", round(body.dimensions.z, 3))


main()
