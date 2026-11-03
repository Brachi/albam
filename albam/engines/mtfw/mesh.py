from contextlib import contextmanager

import bpy

from ...lib.common_op import (
    apply_transform,
    delete_ob,
    move_to_collection
)
from ...lib.export_checks import check_all_objects_have_materials
from ...lib.gltf_blender import export_objects, import_scene, pop_extras
from ...lib.kaitai_utils import parse
from ...lib.scene import EXTRAS_KEY
from ...registry import blender_registry
from ...vfs import VirtualFileData, VirtualFile
from ...exceptions import AlbamCheckFailure
from .bone import get_anim_retarget, get_mirror, set_anim_retarget, set_mirror
from .material import (
    build_blender_materials,
    serialize_materials_data,
    check_mtfw_shader_group,
)
from .mod_scene import (  # noqa: F401  (names other modules import from here)
    APPID_CLASS_MAPPER,
    COLOR_ATTRIBUTE,
    ExportSettings,
    MAIN_LODS,
    MOD_CLASS_MAPPER,
    VERTEX_FORMATS_MAPPER,
    _validate_app_id_for_mod,
    mesh_props_fields,
    mod_to_scene,
    scene_to_mod,
)
from .texture import check_dds_textures

# The names albam gives the UV layers and the vertex color attribute of an
# imported mesh; tools (bake_of_light) and shader setup look them up by name.
UV_LAYER_NAMES = ("uv1", "uv2", "uv3", "uv4")
VERTEX_COLOR_LAYER = "vc"


@blender_registry.register_import_function(app_id="re0", extension="mod", albam_asset_type="MODEL")
@blender_registry.register_import_function(app_id="re1", extension="mod", albam_asset_type="MODEL")
@blender_registry.register_import_function(app_id="re5", extension="mod", albam_asset_type="MODEL")
@blender_registry.register_import_function(app_id="re6", extension="mod", albam_asset_type="MODEL")
@blender_registry.register_import_function(app_id="rev1", extension="mod", albam_asset_type="MODEL")
@blender_registry.register_import_function(app_id="rev2", extension="mod", albam_asset_type="MODEL")
@blender_registry.register_import_function(app_id="dd", extension="mod", albam_asset_type="MODEL")
@blender_registry.register_import_function(app_id="dmc4", extension="mod", albam_asset_type="MODEL")
@blender_registry.register_import_function(app_id="umvc3", extension="mod", albam_asset_type="MODEL")
def build_blender_model(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
    mod_bytes = vfile.get_bytes()
    _validate_app_id_for_mod(app_id, mod_bytes)
    mod = parse(MOD_CLASS_MAPPER[mod_bytes[4]], mod_bytes, app_id)

    import_settings = context.scene.albam.import_settings
    lods = set(MAIN_LODS.get(app_id, ())) if import_settings.import_only_main_lods else None
    bl_object_name = vfile.display_name

    scene = mod_to_scene(app_id, mod, bl_object_name, lods)
    objects = import_scene(scene)
    roots = [ob for ob in objects if ob.parent is None or ob.parent not in objects]
    if len(roots) != 1:
        raise RuntimeError(f"glTF import produced {len(roots)} root objects, expected 1")
    bl_object = roots[0]
    pop_extras(bl_object)
    if bl_object.type == "ARMATURE":
        bl_object.show_in_front = True
        _apply_bone_extras(bl_object, app_id)

    materials = build_blender_materials(vfile, context, mod, bl_object_name)
    for ob in objects:
        if ob.type != "MESH":
            continue
        pop_extras(ob)
        extras = pop_extras(ob.data)
        _name_layers(ob.data)
        _apply_mesh_props(ob.data, app_id, extras.get("mesh_props", {}))
        material = materials.get(extras.get("material_hash"))
        if material is not None:
            ob.data.materials.append(material)
        else:
            print(f"[{bl_object_name}] material {extras.get('material_hash')} not found")
    return bl_object


def _apply_bone_extras(armature_ob, app_id):
    for pose_bone in armature_ob.pose.bones:
        extras = pop_extras(pose_bone.bone)
        pop_extras(pose_bone)
        set_anim_retarget(pose_bone, app_id, str(extras.get("anim_retarget", "")))
        set_mirror(pose_bone, app_id, str(extras.get("mirror", "")))


def _name_layers(bl_mesh):
    for uv_layer, name in zip(bl_mesh.uv_layers, UV_LAYER_NAMES):
        uv_layer.name = name
    color_layer = bl_mesh.color_attributes.get(COLOR_ATTRIBUTE)
    if color_layer is not None:
        color_layer.name = VERTEX_COLOR_LAYER
        bl_mesh.color_attributes.render_color_index = bl_mesh.color_attributes.find(VERTEX_COLOR_LAYER)
        bl_mesh.color_attributes.active_color_index = bl_mesh.color_attributes.render_color_index


def _apply_mesh_props(bl_mesh, app_id, mesh_props):
    custom_properties = bl_mesh.albam_custom_properties.get_custom_properties_for_appid(app_id)
    for attr_name in custom_properties.__annotations__:
        if attr_name not in mesh_props:
            continue
        value = mesh_props[attr_name]
        try:
            setattr(custom_properties, attr_name, value)
        except TypeError:
            # an enum property spells the file's int as a hex string
            try:
                setattr(custom_properties, attr_name, hex(value))
            except TypeError:
                pass


def _gather_mesh_props(bl_mesh, app_id):
    """The mesh custom properties in the file's own types: an enum's hex
    string becomes the int it stands for."""
    custom_properties = bl_mesh.albam_custom_properties.get_custom_properties_for_appid(app_id)
    mesh_props = {}
    for attr_name in custom_properties.__annotations__:
        value = getattr(custom_properties, attr_name)
        if isinstance(value, str):
            try:
                value = int(value, 16)
            except ValueError:
                pass
        mesh_props[attr_name] = value
    return mesh_props


def blender_to_scene(bl_obj, bl_meshes, app_id):
    """The model under `bl_obj` as a Scene, through Blender's glTF exporter,
    with the MT Framework data Blender holds outside the geometry (custom
    properties, bone ids, material names) added to the extras."""
    objects = [bl_obj] + list(bl_meshes)
    scene = export_objects(objects)
    root = scene.roots[0] if len(scene.roots) == 1 else scene.node_named(bl_obj.name)
    root_extras = scene.nodes[root].extras.setdefault(EXTRAS_KEY, {})
    root_extras["app_id"] = app_id
    root_extras["mesh_order"] = [bl_mesh.name for bl_mesh in bl_meshes]
    if bl_obj.type == "ARMATURE":
        root_extras["bone_order"] = [bone.name for bone in bl_obj.data.bones]
        for pose_bone in bl_obj.pose.bones:
            try:
                node = scene.nodes[scene.node_named(pose_bone.name)]
            except KeyError:
                continue
            node.extras[EXTRAS_KEY] = {
                "anim_retarget": get_anim_retarget(pose_bone, app_id),
                "mirror": get_mirror(pose_bone, app_id),
            }
    for bl_mesh in bl_meshes:
        node = scene.nodes[scene.node_named(bl_mesh.name)]
        extras = {
            "mesh_props": _gather_mesh_props(bl_mesh.data, app_id),
        }
        if bl_mesh.data.materials and bl_mesh.data.materials[0] is not None:
            bl_material = bl_mesh.data.materials[0]
            extras["material_name"] = bl_material.name
            material_props = bl_material.albam_custom_properties.get_custom_properties_for_appid(app_id)
            if hasattr(material_props, "vtype"):
                extras["material_props"] = {
                    "vtype": material_props.vtype, "func_skin": material_props.func_skin}
        node.extras[EXTRAS_KEY] = extras
    return scene


def _prepare_color_layers(bl_meshes):
    """Blender's exporter writes the render color attribute as COLOR_0;
    albam's is the one named `vc`, or the first one, the same choice
    get_colors_per_loop made."""
    for bl_mesh in bl_meshes:
        color_attributes = bl_mesh.data.color_attributes
        if not len(color_attributes):
            continue
        index = color_attributes.find(VERTEX_COLOR_LAYER)
        color_attributes.render_color_index = index if index != -1 else 0


def _purge_autofix_leftovers():
    """
    Remove an AlbamTemp left behind by an export that died before cleaning
    up (e.g. a .blend saved after a failure on 0.5.0). Its copies keep their
    original's parent, so they would otherwise be picked up as meshes to
    export; and the collection itself may be excluded from the view layer or
    linked to another scene, which makes apply_transform fail. Dropping the
    whole collection lets move_to_collection create a fresh one.
    """
    temp_collection = bpy.data.collections.get("AlbamTemp")
    if not temp_collection:
        return
    for ob in list(temp_collection.objects):
        delete_ob(ob)
    bpy.data.collections.remove(temp_collection)


@contextmanager
def _autofix_meshes(bl_meshes, enabled):
    # Vertex splitting (one exported vertex per unique attribute
    # combination, see _build_export_vertex_table) and triangulation
    # (see mesh.calc_loop_triangles() in that same function) happen
    # unconditionally at buffer-build time without touching the
    # Blender mesh, so the only "mistake" left to autofix here is an
    # un-applied object transform - which does need a throwaway copy,
    # since applying it is a real mutation.
    if not enabled:
        yield bl_meshes
        return

    duplicates = []
    try:
        for mesh in bl_meshes:
            duplicates.append(_duplicate_mesh_object(mesh))
        move_to_collection(duplicates, "AlbamTemp")
        apply_transform(duplicates)
        yield duplicates
    finally:
        try:
            for ob in duplicates:
                delete_ob(ob)
        finally:
            temp_collection = bpy.data.collections.get("AlbamTemp")
            if temp_collection:
                bpy.data.collections.remove(temp_collection)


@blender_registry.register_export_function(app_id="re0", extension="mod")
@blender_registry.register_export_function(app_id="re1", extension="mod")
@blender_registry.register_export_function(app_id="re5", extension="mod")
@blender_registry.register_export_function(app_id="re6", extension="mod")
@blender_registry.register_export_function(app_id="rev1", extension="mod")
@blender_registry.register_export_function(app_id="rev2", extension="mod")
@blender_registry.register_export_function(app_id="dd", extension="mod")
@blender_registry.register_export_function(app_id="dmc4", extension="mod")
# umvc3 is deliberately absent: .mod geometry round-trips, but the .mrl
# written alongside it does not describe a material this game ships. Every
# one of the 16963 materials in umvc3's own files matches one of 296 distinct
# resource signatures; of the 37 materials exported from the two non-trivial
# models in the serialization dataset, zero do. Export drops the toon
# pipeline the game's look is built on - ttoonmap, ftoonlightcalc,
# cbhalflambert, cbdiffusecolorcorect - and invents fambient/focclusion/
# femission in its place, so the engine would be handed shader permutations
# no shipped content uses. Import is unaffected and stays registered.
#
# Re-register together with the .mrl work, gated on that measurement rather
# than on resource counts: exported signatures should be found in the
# shipped set. See docs on albam-wip's mrl-export-overhaul branch, whose
# bugs 3, 4, 7 and 9 are the same code.
@check_dds_textures
@check_mtfw_shader_group
@check_all_objects_have_materials
def export_mod(bl_obj):
    export_settings = bpy.context.scene.albam.export_settings
    asset = bl_obj.albam_asset
    app_id = asset.app_id

    ModCls = APPID_CLASS_MAPPER[app_id]
    src_mod = parse(ModCls, asset.original_bytes, app_id)
    # Before collecting meshes, so stale copies are not among them.
    _purge_autofix_leftovers()
    # TODO: export options like visibility
    bl_meshes = [c for c in bl_obj.children_recursive if c.type == "MESH"]
    if export_settings.export_visible:
        bl_meshes = [mesh for mesh in bl_meshes if mesh.visible_get()]
    if not bl_meshes:
        raise AlbamCheckFailure(
            "There is no mesh to export",
            details=f"Object '{bl_obj.name}' has no visible mesh children"
            if export_settings.export_visible else
            f"Object '{bl_obj.name}' has no mesh children",
            solution="Unhide the meshes and/or parent them to the exported object "
            f"'{bl_obj.name}', or disable 'Export only visible meshes' if that's hiding them"
        )
    _check_armature_modifiers_target(bl_obj, bl_meshes)
    _check_armature_modifiers_present(bl_obj, bl_meshes)

    settings = ExportSettings(
        export_bones=export_settings.export_bones,
        no_vf_grouping=export_settings.no_vf_grouping,
        force_lod255=export_settings.force_lod255,
        force_max_num_weights=export_settings.force_max_num_weights,
    )
    serialized = {}

    def serialize_materials(dst_mod):
        materials_map, mrl, vtextures = serialize_materials_data(asset, bl_meshes, src_mod, dst_mod)
        serialized["mrl"] = mrl
        serialized["vtextures"] = vtextures
        return materials_map

    with _autofix_meshes(bl_meshes, export_settings.export_autofix) as bl_meshes:
        _prepare_color_layers(bl_meshes)
        scene = blender_to_scene(bl_obj, bl_meshes, app_id)
        mod_bytes = scene_to_mod(scene, src_mod, app_id, settings, serialize_materials)

    vfiles = [VirtualFileData(app_id, asset.relative_path, data_bytes=mod_bytes)]
    vfiles.extend(serialized["vtextures"])
    if serialized["mrl"]:
        vfiles.append(serialized["mrl"])
    return vfiles


def _check_armature_modifiers_present(bl_obj, bl_meshes):
    if bl_obj.type != "ARMATURE":
        return
    for bl_mesh in bl_meshes:
        if not any(m.type == "ARMATURE" and m.object for m in bl_mesh.modifiers):
            raise AlbamCheckFailure(
                "The mesh object has no Armature modifier",
                details=f"Object: {bl_mesh.name}",
                solution="Please add Armature modifier and set imported skeleton as Object"
            )


def _check_armature_modifiers_target(bl_obj, bl_meshes):
    """Every Armature modifier has to deform with the rig being exported.

    Bone palettes are built from the exported armature's bone order, while
    vertex weights are read through the mesh's Armature modifier. If the
    modifier points at another armature, the two orders disagree and export
    fails much later with a bare "ValueError: 29 is not in list" (#335).
    """
    if bl_obj.type != 'ARMATURE':
        return
    for bl_mesh in bl_meshes:
        for modifier in bl_mesh.modifiers:
            if modifier.type != 'ARMATURE' or modifier.object is None:
                continue
            if modifier.object != bl_obj:
                raise AlbamCheckFailure(
                    "A mesh is deformed by a different armature than the one being exported",
                    details=f"Object: {bl_mesh.name}, Armature modifier '{modifier.name}' "
                    f"points to '{modifier.object.name}', exported armature: '{bl_obj.name}'",
                    solution=f"Set the Armature modifier's Object to '{bl_obj.name}'"
                )


# num_vertices and last_index are each a u2 on every mod version (mod_21,
# mod_153, mod_156). last_index is current_vertex_position (the running
# total across every mesh sharing one vertex block, see no_vf_grouping
# below) plus this mesh's own count minus one, so it overflows when meshes
# add up; num_vertices overflows on its own for a single mesh of exactly
# 65536 vertices, where last_index still fits. Either way Kaitai's
# write_u2le would raise a bare struct.error naming neither the mesh nor
# the field.
MAX_MESH_U2 = 0xFFFF


def _duplicate_mesh_object(src_obj):
    """
    A plain, independent copy of `src_obj` (own object + own mesh
    datablock), so autofix's apply_transform can mutate it without touching
    the user's original object.
    """
    dst_obj = src_obj.copy()
    dst_obj.data = src_obj.data.copy()
    bpy.context.collection.objects.link(dst_obj)
    return dst_obj


@blender_registry.register_custom_properties_mesh("mod_156_mesh", ("re5", "dmc4"))
@blender_registry.register_blender_prop
class Mod156MeshCustomProperties(bpy.types.PropertyGroup):
    vdecl_enum = bpy.props.EnumProperty(
        name="",
        description="",
        items=[
            ("0x0", "VDECL_SKIN", "", 1),
            ("0x1", "VDECL_NONSKIN", "", 2),
            ("0x2", "VDECL_SKINEX", "", 3),
            ("0x3", "VDECL_FILTER", "", 4),
            ("0x4", "VDECL_FILTER2", "", 5),
            ("0x5", "VDECL_SKIN_BASE", "", 6),
            ("0x6", "VDECL_NONSKIN_BASE", "", 7),
            ("0x7", "VDECL_SKINEX_BASE", "", 8),
            ("0x8", "VDECL_NONSKIN_COL", "", 9),
            ("0x9", "VDECL_NONSKIN_COLEX", "", 10),
            ("0xa", "VDECL_SHAPE_BASE", "", 11),
            ("0xb", "VDECL_SHAPE", "", 12),
            ("0xc", "VDECL_SKIN_COL", "", 13),
            ("0xd", "VDECL_MATERIAL", "", 14),
            ("0xe", "VDECL_SKINSO", "", 15),
            ("0xf", "VDECL_I2GLINE", "", 16),
            ("0x10", "VDECL_NUM", "", 17),
        ],
        default="0x0",
        options=set()
    )
    level_of_detail: bpy.props.IntProperty(name="Level of Detail", default=255, options=set())  # noqa: F821
    idx_group: bpy.props.IntProperty(name="Group ID", default=0, options=set())  # noqa: F821
    alpha_priority: bpy.props.IntProperty(name="Alpha Transparency Priority",
                                          default=0, options=set())  # noqa: F821
    shape: bpy.props.BoolProperty(name="Shape", default=0, options=set())   # noqa: F821
    reserved2_flag_1: bpy.props.BoolProperty(name="Reserved 1", default=0, options=set())  # noqa: F821
    reserved2_flag_2: bpy.props.BoolProperty(name="Reserved 2", default=0, options=set())  # noqa: F821
    env: bpy.props.BoolProperty(name="Environment", default=1, options=set())  # noqa: F821
    refrect: bpy.props.BoolProperty(name="Reflect", default=1, options=set())  # noqa: F821
    shadow_cast: bpy.props.BoolProperty(name="Cast Shadow", default=1, options=set())  # noqa: F821
    shadow_receive: bpy.props.BoolProperty(name="Receive Shadow", default=1, options=set())  # noqa: F821
    sort: bpy.props.BoolProperty(name="Sorting", default=0, options=set())  # noqa: F821
    vdeclbase: vdecl_enum
    vdecl: vdecl_enum
    rcn_base: bpy.props.IntProperty(name="RCN Base", default=0, options=set())  # noqa: F821
    boundary: bpy.props.IntProperty(name="Boundary", default=0, options=set())  # noqa: F821

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            if type(getattr(self, attr_name)) is str:
                setattr(dst_obj, attr_name, int(getattr(self, attr_name), 16))
            else:
                setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except TypeError:
                setattr(self, attr_name, hex(getattr(src_obj, attr_name)))


VERTEX_FORMATS_LABELS = {
    0x4325a03e: "NonSkinTBN_4M",  # shape keys not implemented yet
    0xa14e003c: "NonSkinBCA",
    0x2082f03b: "NonSkinBLA",
    0xc66fa03a: "NonSkinBA",
    0xd1a47038: "NonSkinBL",
    0x207d6037: "NonSkinBC",
    0xa7d7d036: "NonSkinB",
    0x37a4e035: "NonSkinTBNLA",
    0xb6681034: "NonSkinTBNCA",
    0x9399c033: "NonSkinTBCA",
    0x12553032: "NonSkinTBLA",
    0x747d1031: "NonSkinTBNA",
    0x63b6c02f: "NonSkinTBNL",
    0x926fd02e: "NonSkinTBNC",
    0xafa6302d: "NonSkinTBA",
    0x5e7f202c: "NonSkinTBN",
    0xb86de02a: "NonSkinTBL",
    0x49b4f029: "NonSkinTBC",
    0xd8297028: "NonSkinTB",
    0xcbcf7027: "SkinTBNLA8wt",
    0xd84e3026: "SkinTBC8wt",
    0x75c3e025: "SkinTBN8wt",
    0xbb424024: "SkinTB8wt",
    0x64593023: "SkinTBNLA4wt",
    0x77d87022: "SkinTBC4wt",
    0xdA55a021: "SkinTBN4wt",
    0x14d40020: "SkinTB4wt",
    0xb392101f: "SkinTBNLA2wt",
    0xa013501e: "SkinTBC2wt",
    0xd9e801d: "SkinTBN2wt",
    0xc31f201c: "SkinTB2wt",
    0xd877801b: "SkinTBNLA1wt",
    0xcbf6c01a: "SkinTBC1wt",
    0x667b1019: "SkinTBN1wt",
    0xa8fab018: "SkinTB1wt",
    0x2f55c03d: "SkinOTB_4WT_4M",  # shape keys are not implemented yet
    0xa320c016: "Bridge8wt",
    0xcb68015: "Bridge4wt",
    0xdb7da014: "Bridge2wt",
    0xb0983013: "Bridge1wt",
}

vertex_format_enum_items = [
    (
        hex(key),  # value
        label,     # label
        f"{label} ({hex(key)})",  # description
        idx
    )
    for idx, (key, label) in enumerate(VERTEX_FORMATS_LABELS.items())
]


@blender_registry.register_custom_properties_mesh("mod_21_mesh",
                                                  ("re0", "re1", "re6", "rev1", "rev2", "dd", "umvc3"))
@blender_registry.register_blender_prop
class Mod21MeshCustomProperties(bpy.types.PropertyGroup):
    level_of_detail: bpy.props.IntProperty(name="Level of Detail", default=255, options=set())  # noqa: F821
    draw_mode: bpy.props.IntProperty(name="Draw Mode", default=0, options=set())  # noqa: F821  TODO: b12
    idx_group: bpy.props.IntProperty(name="Group ID", default=0, options=set())  # noqa: F821
    disp: bpy.props.BoolProperty(name="Display Mesh in Game", default=1, options=set())  # noqa: F821
    shape: bpy.props.BoolProperty(name="Shape", default=0, options=set())  # noqa: F821
    sort: bpy.props.BoolProperty(name="Sorting", default=0, options=set())  # noqa: F821
    alpha_priority: bpy.props.IntProperty(name="Alpha Transparency Priority",  # noqa: F821
                                          default=0, options=set())  # TODO b8
    topology: bpy.props.IntProperty(name="Topology", default=0, options=set())  # noqa: F821  TODO b6
    binormal_flip: bpy.props.BoolProperty(name="Binormal Flip", default=0, options=set())  # noqa: F821
    bridge: bpy.props.BoolProperty(name="Bridge Geometry", default=0, options=set())  # noqa: F821
    bone_id_start: bpy.props.IntProperty(name="Bone ID Start", default=0, options=set())  # noqa: F821
    connect_id: bpy.props.IntProperty(name="Connect ID", default=0, options=set())  # noqa: F821
    boundary: bpy.props.IntProperty(name="Boundary", default=0, options=set())  # noqa: F821
    #  vertex_format: bpy.props.StringProperty(name="Vertex Format", options=set())  # noqa: F821
    vertex_format: bpy.props.EnumProperty(
        name="Vertex Format",  # noqa: F821
        description="Vertex format (MT Framework)",
        items=vertex_format_enum_items,
        options=set()
    )

    # FIXME: dedupe
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    # FIXME: dedupe
    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except TypeError:
                pass
                # print(f"Type mismatch {attr_name}, {src_obj}")
