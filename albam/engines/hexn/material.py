import io
import os

import bpy
from kaitaistruct import KaitaiStream

from .texture import build_blender_textures, _texture_suffix
from .structs.hexane_matb import HexaneMatb
from ...lib.blender import layout_node_chains

# A .matb's texture paths end in a two-character suffix identifying their
# role (e.g. "..._skel_d.dds", "..._skel_n.dds") - confirmed against a
# full-game sweep, see matb.ksy/tests/hexn/test_matb_parsing.py. Maps each
# suffix to the Principled BSDF input it feeds and the color space its DDS
# should be read as (data maps like normal/specular aren't color, so must
# be Non-Color or Blender's color management will darken them). Only these
# four are wired up here; other suffixes seen in the wild (roughness/mask/
# env-map-like ones) aren't handled yet.
TEXTURE_SLOTS = {
    "_d": ("Base Color", "sRGB"),
    "_n": ("Normal", "Non-Color"),
    "_s": ("Specular IOR Level", "Non-Color"),
    "_g": ("Emission Color", "sRGB"),
}


def build_blender_materials(edgemodel, context, root_id=None):

    material_paths = set()
    matbs = []
    bl_materials = {}
    texture_paths = set()

    for mesh_header in edgemodel.meshes_header:
        path = mesh_header.materials.first_material
        material_paths.add(path)

    vfs = context.scene.albam.vfs

    for material_path in material_paths:
        # A .matb a mesh names doesn't have to be reachable: shared
        # surfaces live in their own archives, so mounting a single .ssg
        # (the UI's "Add Files") legitimately leaves some unresolvable.
        # Import what's there rather than failing outright - same
        # tolerate-absence convention as skeleton._find_skel_vfile.
        #
        # root_id prefers the model's own mounted root: different packs
        # can each happen to use this same material path for an unrelated
        # file, and without it a lookup could silently resolve to whichever
        # root's copy was added first (see vfs.get_vfile's own docstring).
        try:
            matb_vfile = vfs.get_vfile("reorc", material_path, root_id=root_id)
        except KeyError:
            print(f"[{material_path}] material not found, skipping")
            continue
        matb_bytes = matb_vfile.get_bytes()
        matb = HexaneMatb(KaitaiStream(io.BytesIO(matb_bytes)))
        matb._read()
        matbs.append((matb, material_path))
        for texture_path in matb.shader.textures:
            if _texture_suffix(texture_path) in TEXTURE_SLOTS:
                texture_paths.add(texture_path)

    tex_mapping = build_blender_textures(texture_paths, context, root_id=root_id)

    for matb, material_path in matbs:
        if not matb.shader.textures:
            continue

        bl_material = bpy.data.materials.new(os.path.basename(material_path))
        bl_material.use_nodes = True
        # Same as MT Framework's own materials (albam.engines.mtfw.material) -
        # a _d diffuse map's Alpha is wired below whenever the texture has
        # one (hair cards etc. use it as a cutout mask; solid DXT1 diffuse
        # maps decode Alpha as a flat 1.0, so this is a no-op for those).
        # Blender 5.x accepts "CLIP" here but stores HASHED - the
        # per-material control it kept is alpha_threshold, with dithered
        # vs blended now living on the material's render method. Set the
        # same way albam.engines.mtfw.material does.
        bl_material.blend_method = "CLIP"
        node_tree = bl_material.node_tree
        bsdf = next(node for node in node_tree.nodes if node.type == "BSDF_PRINCIPLED")
        link = node_tree.links.new
        node_chains = []

        for texture_path in matb.shader.textures:
            slot = TEXTURE_SLOTS.get(_texture_suffix(texture_path))
            if slot is None:
                continue
            socket_name, color_space = slot
            bl_image = tex_mapping.get(texture_path)
            if bl_image is None:  # unreachable texture, already reported
                continue
            bl_image.colorspace_settings.name = color_space

            texture_node = node_tree.nodes.new("ShaderNodeTexImage")
            texture_node.image = bl_image
            texture_node.label = os.path.basename(texture_path)

            if socket_name == "Normal":
                normal_map_node = node_tree.nodes.new("ShaderNodeNormalMap")
                # RE:ORC is DirectX9-era (Y-down/green-down normal maps);
                # Blender's default convention is OpenGL (Y-up). The texture
                # itself is still the raw, unswizzled DXT5nm data (see
                # texture.py's _build_unswizzled_normal_image) - this is the
                # only place the DirectX/OpenGL Y difference gets handled.
                normal_map_node.convention = "DIRECTX"
                link(texture_node.outputs["Color"], normal_map_node.inputs["Color"])
                link(normal_map_node.outputs["Normal"], bsdf.inputs["Normal"])
                node_chains.append([texture_node, normal_map_node])
            elif socket_name == "Specular IOR Level":
                link(texture_node.outputs["Color"], bsdf.inputs[socket_name])
                # _s is DXT5 (unlike _d's DXT1 - no alpha needed there), and its
                # Alpha channel carries real per-texel variation distinct from
                # RGB (checked against real character textures: alpha isn't
                # flat, and while it correlates with RGB luminance it isn't
                # identical to it) - matching the classic DirectX9-era
                # convention this specular map's format otherwise fits: RGB
                # specular color/intensity, Alpha specular power/gloss. Invert
                # because a bright/glossy value means low roughness. Without
                # this, Roughness stays at the Principled BSDF's flat 0.5
                # default for every material, regardless of how shiny/matte
                # the specular map says a surface actually is.
                invert_node = node_tree.nodes.new("ShaderNodeInvert")
                link(texture_node.outputs["Alpha"], invert_node.inputs["Color"])
                link(invert_node.outputs["Color"], bsdf.inputs["Roughness"])
                node_chains.append([texture_node, invert_node])
            else:
                link(texture_node.outputs["Color"], bsdf.inputs[socket_name])
                if socket_name == "Emission Color":
                    bsdf.inputs["Emission Strength"].default_value = 1.0
                elif socket_name == "Base Color":
                    link(texture_node.outputs["Alpha"], bsdf.inputs["Alpha"])
                node_chains.append([texture_node])

        layout_node_chains(bsdf, node_chains)
        bl_materials[material_path] = bl_material

    return bl_materials
