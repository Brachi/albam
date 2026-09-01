from io import BytesIO
from kaitaistruct import KaitaiStream
import bpy
from mathutils import Vector
import math
from ...registry import blender_registry
from ...vfs import VirtualFile, VirtualFileData
from ...lib.misc import chunks
from ...exceptions import AlbamCheckFailure
from .structs.re4_uhd_bin import Re4UhdBin
from .material import build_blender_materials


# Bones are stored as LOCAL offsets from parent in millimeters (confirmed via debug:
# bone_000 raw_y=1140 = 1.14m hip height, bone_004 accumulated = 1.65m chest).
GLOBAL_SCALE = 0.001  # same raw unit as vertex positions
GLOBAL_NORMAL_FIX_EXTENDED = 545460800000
GLOBAL_NORMAL_FIX_REDUCED = 16384

# Header layout. The format allows 0x40, 0x50 and 0x60 headers - the shorter
# ones simply stop before the trailing offsets - and offset_bones doubles as
# the header's own size.
HEADER_SIZE = 0x60
BONE_SIZE = 16
WEIGHT_SIZE = 8
VEC3_SIZE = 12
UV_SIZE = 8
RGBA_SIZE = 4
INDEX_SIZE = 2
MATERIAL_SIZE = 24

# The flags word at 0x20. 0x80000000 is set on every mesh .bin and on nothing
# else, which is what tells a mesh apart from the camera and lighting data
# that share the extension.
BIN_FLAG_IS_MESH = 0x80000000
BIN_FLAG_VERTEX_COLORS = 0x40000000
BIN_FLAG_ALT_NORMALS = 0x20000000
BIN_FLAG_ADJACENCY = 0x00000200
BIN_FLAG_BONEPAIRS = 0x00000100

# Build stamps, shipped as exactly these two values: the first where the
# bonepair and adjacency blocks are present, the second where they are not.
VERSION_FLAGS_WITH_TAGS = 0x20030818
VERSION_FLAGS_PLAIN = 0x20010801

NO_PARENT = 0xFF
NO_TEXTURE = 0xFF
MAX_BONE_INFLUENCES = 3
# Both counts are u2, and every triangle costs three corners of its own.
MAX_VERTICES = 0xFFFF
MAX_TRIANGLES_PER_STRIP = 0xFFFF // 3

FTYPE_TRIANGLE_LIST = 5

_MATERIAL_BYTE_FIELDS = (
    "unk_min_11", "unk_min_10", "unk_min_09", "unk_min_08", "unk_min_07",
    "unk_min_06", "unk_min_05", "unk_min_04", "unk_min_03", "unk_min_02",
    "unk_min_01", "material_flag", "diffuse_map", "intensity_specular_r",
    "intensity_specular_g", "intensity_specular_b", "unk_00", "unk_01",
    "specular_scale", "unk_02",
)
_MATERIAL_NO_TEXTURE_FIELDS = (
    "bump_map", "opacity_map", "generic_specular_map", "custom_specular_map",
)
# Which shader-group input each of the material's texture slots is wired to
# on import (see engines/cie/material.py). Read back the same way on export,
# so a texture swapped in Blender is the one that gets written.
_TEXTURE_SLOT_INPUTS = (
    ("diffuse_map", "Diffuse BM"),
    ("bump_map", "Normal NM"),
    ("opacity_map", "Alpha BM"),
    ("custom_specular_map", "Special MM"),
)

# face_index primitive types (RE4 UHD BIN format, same as DirectX D3DPT_* values)
FCOUNT_TYPES = {
    5: "FTYPE_TRIANGLE_LIST",  # fcount/3 triangles, 3 sequential verts per triangle
    6: "FTYPE_TRIANGLE_STRIP",  # fcount-2 triangles, alternating winding
    7: "FTYPE_TRIANGLE_FAN",  # fcount-2 triangles, fan around first vertex
    8: "FTYPE_QUAD_LIST",  # fcount/4 quads, each split into 2 triangles
}


def _validate_bin_mesh(bin_bytes, bl_object_name):
    # .BIN extension is misleading, different types of files (like camera, lighting) use it too
    # The simplest size check with the mesh .bin header should to sift out the imposters
    re4uhd_bin_mesh_hdr_size = 80
    if len(bin_bytes) < re4uhd_bin_mesh_hdr_size:
        raise AlbamCheckFailure(
            f"The {bl_object_name}' is not a valid mesh BIN file and probably contains a non-geometry data",
            details=f"The file is smaller than a minimum size {re4uhd_bin_mesh_hdr_size} bytes",
            solution="Select another .BIN file"
        )


@blender_registry.register_import_function(app_id="re4uhd", extension="bin", albam_asset_type="MODEL")
def build_blender_model(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    bin_bytes = vfile.get_bytes()
    bl_object_name = vfile.display_name

    _validate_bin_mesh(bin_bytes, bl_object_name)

    bin = Re4UhdBin.from_bytes(bin_bytes)
    bin._read()
    locations = [_yz_flip(v.x, v.y, v.z) for v in bin.vertex_positions]
    faces, mat_face_ranges = _build_faces(bin)

    bl_mesh = bpy.data.meshes.new(bl_object_name)
    bl_mesh.from_pydata(locations, [], faces)
    bl_mesh.update()

    if bin.texcoords:
        uv_layer = bl_mesh.uv_layers.new(name="uv")
        for loop in bl_mesh.loops:
            uv = bin.texcoords[loop.vertex_index]
            uv_layer.data[loop.index].uv = (uv.u, 1.0 - uv.v)  # flip V for Blender

    if bin.normals:
        loop_normals = []
        for loop in bl_mesh.loops:
            n = bin.normals[loop.vertex_index]
            # loop_normals.append(_yz_flip(n.x, n.y, n.z))
            loop_normals.append(_decode_normal(n))
        bl_mesh.normals_split_custom_set(loop_normals)
    bl_mesh.normals_split_custom_set(loop_normals)

    bl_mesh.albam_custom_properties.get_custom_properties_for_appid(
        "re4uhd").set_from_source(bin.header)
    _apply_materials(bl_mesh, bin, mat_face_ranges, _resolve_tpl(vfile, bin, context))
    bl_mesh_ob = bpy.data.objects.new(f"{bl_object_name}.000", bl_mesh)
    _build_shape_keys(bl_mesh_ob, bin)

    # usually only one armature is full, other bin files include only bones used by the mesh
    shared_armature = bpy.context.scene.albam.import_options_bin.shared_armature
    root_vfile = vfile.root_vfile
    skeleton = _build_armature(bl_object_name, bin, context, shared_armature,
                               archive_id=root_vfile.name if root_vfile else "")

    if skeleton:
        _apply_weights(bl_mesh_ob, bin)
        arm_mod = bl_mesh_ob.modifiers.new("Armature", 'ARMATURE')
        arm_mod.object = skeleton
        arm_mod.use_vertex_groups = True

    if skeleton and not shared_armature:
        bl_object = skeleton
    else:
        bl_object = bpy.data.objects.new(bl_object_name, None)
        context.collection.objects.link(bl_object)

    # Linking is what puts an object in the scene: one that only exists in
    # bpy.data is invisible in the viewport and absent from renders, even
    # though it has geometry and shows up in bpy.data.objects. The armature
    # was already linked in _build_armature, so before this a character
    # imported as a skeleton with nothing on it.
    context.collection.objects.link(bl_mesh_ob)
    bl_mesh_ob.parent = bl_object
    return bl_object


@blender_registry.register_custom_properties_mesh("bin_cie_mesh", ("re4uhd",))
@blender_registry.register_blender_prop
class BinCIEMeshCustomProperties(bpy.types.PropertyGroup):
    """Header values a Blender mesh has nowhere else to keep.

    Everything else in the header is either geometry Blender holds directly
    or an offset the exporter computes, so only these survive a round trip by
    being stored here rather than read back off the file being replaced.
    """
    # The exponent of the divisor morph deltas are stored against:
    # delta / 2 ** vertex_scale.
    vertex_scale: bpy.props.IntProperty(name="Vertex Scale", default=0, options=set())  # noqa: F821
    # How many TPL slots the materials address. The count is what pairs a
    # model with the right .tpl in its archive.
    num_tpl: bpy.props.IntProperty(name="TPL Slots", default=0, options=set())  # noqa: F821

    def set_from_source(self, bin_header):
        self.vertex_scale = bin_header.vertex_scale
        self.num_tpl = bin_header.num_tpl


def _yz_flip(x, y, z):
    """Convert Y-up (RE4, milimeters) to Z-up (Blender, meters)."""
    return (x * GLOBAL_SCALE, -z * GLOBAL_SCALE, y * GLOBAL_SCALE,)


def _zy_flip(x, y, z):
    """Convert Z-up (Blender, meters) to Y-up (RE4, millimeters).

    The exact inverse of _yz_flip: that maps (X, Y, Z) to (X, -Z, Y), so
    coming back means (x, z, -y), not (x, y, -z).
    """
    return (x / GLOBAL_SCALE, z / GLOBAL_SCALE, -y / GLOBAL_SCALE)


def _build_shape_keys(bl_ob, bin):
    if not bin.morphs:
        return
    extra_scale = 2 ** bin.header.vertex_scale

    def _yz_flip_scaled(x, y, z):
        return ((x / extra_scale), (z / extra_scale), (y / extra_scale))

    bl_ob.shape_key_add(name="Basis", from_mix=False)
    for i, mgroup in enumerate(bin.morphs.morph_groups):
        sk = bl_ob.shape_key_add(name=str(i).zfill(3), from_mix=False)
        for i, vtx in enumerate(mgroup.body.vertices):
            vtx_shift = _yz_flip_scaled(vtx.position.x,
                                        vtx.position.y,
                                        vtx.position.z)
            sk.data[vtx.id].co.x += vtx_shift[0] * GLOBAL_SCALE
            sk.data[vtx.id].co.y += vtx_shift[1] * GLOBAL_SCALE
            sk.data[vtx.id].co.z += vtx_shift[2] * GLOBAL_SCALE


def _decode_normal(n):
    normal_fix = math.sqrt(n.x ** 2 + n.y ** 2 + n.z ** 2)
    if normal_fix == 0:
        normal_fix = 1
    return (n.x / normal_fix, n.z / normal_fix * -1, n.y / normal_fix)


def _encode_normal(vector, n, extended=True):
    NORMAL_FIX = GLOBAL_NORMAL_FIX_EXTENDED if extended else GLOBAL_NORMAL_FIX_REDUCED
    vector.x = n.x * NORMAL_FIX
    vector.y = n.z * NORMAL_FIX
    vector.z = - n.y * NORMAL_FIX


def _build_faces(bin):
    # RE4 UHD uses a non-indexed mesh layout: vertex_positions has one entry
    # per face-corner (no vertex sharing). Faces are formed by consuming vertices
    # sequentially, grouped per material and per strip within each material.
    faces = []
    mat_face_ranges = []
    vertex_offset = 0

    for mat_i, material in enumerate(bin.materials):
        fi = material.face_index
        mat_start = len(faces)

        for strip in fi.strips:
            verts = list(range(vertex_offset, vertex_offset + strip.fcount))
            vertex_offset += strip.fcount
            _process_strip(faces, verts, strip.ftype)

        mat_face_ranges.append((mat_start, len(faces)))

    return faces, mat_face_ranges


def _process_strip(faces, verts, ftype):
    """Append triangles from a single strip to the faces list."""
    ftype_str = FCOUNT_TYPES.get(ftype, "")
    match ftype_str:
        case "FTYPE_TRIANGLE_LIST":
            # Each consecutive triplet = one triangle
            for tri in chunks(verts, 3):
                if len(tri) == 3 and tri[0] != tri[1] and tri[0] != tri[2] and tri[1] != tri[2]:
                    faces.append(tuple(tri))
        case "FTYPE_TRIANGLE_STRIP":
            # Triangle strip with alternating winding
            if len(verts) < 3:
                return
            bkface = -1
            p1, p2, p3 = verts[0], verts[1], verts[2]
            bkface = -bkface  # -> 1
            if p1 != p2 and p1 != p3 and p2 != p3:
                faces.append((p1, p2, p3))
            for i in range(1, len(verts) - 2):
                bkface = -bkface
                p1, p2, p3 = p2, p3, verts[i + 2]
                if p1 != p2 and p1 != p3 and p2 != p3:
                    if bkface == 1:
                        faces.append((p1, p2, p3))
                    else:
                        faces.append((p3, p2, p1))

        case "FTYPE_TRIANGLE_FAN":
            # Fan around the first vertex
            center = verts[0]
            for i in range(2, len(verts)):
                p1, p2, p3 = center, verts[i - 1], verts[i]
                if p1 != p2 and p1 != p3 and p2 != p3:
                    faces.append((p1, p2, p3))
        case "FTYPE_QUAD_LIST":
            # Each group of 4 verts = 1 quad = 2 triangles
            for quad in chunks(verts, 4):
                if len(quad) == 4:
                    p1, p2, p3, p4 = quad
                    if p1 != p2 and p1 != p3 and p2 != p3:
                        faces.append((p1, p2, p3))
                    if p1 != p3 and p1 != p4 and p3 != p4:
                        faces.append((p1, p3, p4))
        case _:
            print(f"[re4uhd] WARNING: unknown ftype={ftype}, {len(verts)} verts skipped")


def _apply_materials(bl_mesh, bin, mat_face_ranges, tpl_vfile):
    build_blender_materials(bl_mesh, bin, tpl_vfile)
    for mat_i, (start, end) in enumerate(mat_face_ranges):
        for fi in range(start, end):
            bl_mesh.polygons[fi].material_index = mat_i


ARCHIVE_PROPERTY = "cie.source_archive"


def _find_reusable_armature(bin, context, archive_id):
    """An armature already imported from `archive_id` that covers every bone
    this model uses, or None.

    A character archive holds one model carrying the whole skeleton and many
    carrying only the bones they need - a head, a hand, a level-of-detail
    copy. Importing them one after another otherwise leaves a scene full of
    part-skeletons that don't move together; reusing the fullest one binds
    every part to the same rig.

    Scoped to the archive it came from because bone ids are per-model
    integers, not names: every character in the game numbers its bones from
    0, so two characters in one scene would look like each other's skeletons.
    """
    needed = {str(bone.bone_id) for bone in bin.bones}
    best = None
    for bl_object in context.scene.objects:
        if bl_object.type != "ARMATURE":
            continue
        if bl_object.get(ARCHIVE_PROPERTY) != archive_id:
            continue
        names = {bone.name for bone in bl_object.data.bones}
        if needed <= names and (best is None or len(names) > len(best.data.bones)):
            best = bl_object
    return best


def _build_armature(bl_object_name, bin, context, shared_armature=None, archive_id=None):
    """Create an armature object from BIN bones and return it, or None if no bones."""
    if not bin.bones:
        return None

    existing = shared_armature
    if existing is None and archive_id:
        existing = _find_reusable_armature(bin, context, archive_id)
    if existing:
        print(f"[re4uhd] armature: reusing '{existing.name}' ({len(bin.bones)} bones)")
        return existing

    bone_data = {b.bone_id: b for b in bin.bones}

    def world_pos(bone_id, visited=None):
        """Recursively accumulate local offsets (same unit as vertices) to world position."""
        if visited is None:
            visited = set()
        if bone_id in visited:
            return Vector((0.0, 0.0, 0.0))
        visited.add(bone_id)
        b = bone_data[bone_id]
        # Y-up (RE4) -> Z-up (Blender), game units -> Blender meters
        local = Vector((b.x * GLOBAL_SCALE, -b.z * GLOBAL_SCALE, b.y * GLOBAL_SCALE))
        if b.parent == b.bone_id or b.parent not in bone_data:
            return local
        return world_pos(b.parent, visited) + local

    world_positions = {b.bone_id: world_pos(b.bone_id) for b in bin.bones}

    arm_data = bpy.data.armatures.new(f"{bl_object_name}_armature")
    arm_ob = bpy.data.objects.new(f"{bl_object_name}_armature", arm_data)
    arm_ob[ARCHIVE_PROPERTY] = archive_id or ""
    context.collection.objects.link(arm_ob)

    # Use bpy.ops with a reliable override to enter edit mode
    prev_active = context.view_layer.objects.active

    context.view_layer.objects.active = arm_ob
    bpy.ops.object.mode_set(mode='EDIT')

    edit_bone_map = {}
    # Create bones
    for bone in bin.bones:
        blender_bone = arm_data.edit_bones.new(f"{bone.bone_id}")
        blender_bone['cie.anim_retarget'] = str(bone.bone_id)
        head = world_positions[bone.bone_id]
        blender_bone.head = head
        children = [c for c in bin.bones
                    if c.parent == bone.bone_id and c.bone_id != bone.bone_id]
        if children:
            child_avg = sum((world_positions[c.bone_id] for c in children), Vector((0, 0, 0)))
            child_avg /= len(children)
            blender_bone.tail = (child_avg if (child_avg - head).length > 0.001
                                 else head + Vector((0, 0, 0.02)))
        else:
            blender_bone.tail = head + Vector((0, 0, 0.02))

        edit_bone_map[bone.bone_id] = blender_bone

    for bone in bin.bones:
        if bone.parent != bone.bone_id and bone.parent in edit_bone_map:
            edit_bone_map[bone.bone_id].parent = edit_bone_map[bone.parent]
            edit_bone_map[bone.bone_id].use_connect = False

    bpy.ops.object.mode_set(mode='OBJECT')
    context.view_layer.objects.active = prev_active

    # Show bones in front of the mesh (same style as MT Framework armatures in albam)
    arm_ob.show_in_front = True
    arm_data.display_type = 'STICK'
    return arm_ob


def _apply_weights(mesh_ob, bin):
    """
    Create vertex groups and assign bone weights.

    bin.indexes[i]  = value is the index j for weights table bin.weights[j]
    bin.weights[j]  = WeightMap entry: up to 3 (bone_id, weight/255) pairs;
                      count tells how many bones are active (1-3).
    """
    if not bin.weights or not bin.indexes:
        return

    weight_index = list(bin.indexes)
    weight_maps = list(bin.weights)
    vg_cache = {}  # bone_id -> VertexGroup

    def get_vg(bone_id):
        name = f"{bone_id}"
        if name not in vg_cache:
            vg_cache[name] = mesh_ob.vertex_groups.new(name=name)
        return vg_cache[name]

    for vert_i, wm_idx in enumerate(weight_index):
        if wm_idx >= len(weight_maps):
            continue
        wm = weight_maps[wm_idx]

        # Collect active bone weights and normalize so they sum to 1.0.
        # Weights are stored as raw bytes (0-255) whose sum may not equal 255.
        # Dividing by actual sum ensures full vertex coverage.
        active = []
        for i in range(wm.count):
            active.append((wm.bone_ids[i], wm.weights[i]))

        total = sum(w for _, w in active)
        if total == 0:
            continue

        for bone_id, raw_w in active:
            get_vg(bone_id).add([vert_i], raw_w / total, 'REPLACE')

    print(f"[re4uhd] weights: {len(weight_index)} verts, {len(vg_cache)} vertex groups")


AUTO_TPL = "__auto__"


def _tpl_entry_count(vfile):
    """How many texture slots a .tpl has, or None if it won't parse."""
    from .structs.tpl import Tpl
    try:
        tpl = Tpl.from_bytes(vfile.get_bytes())
        tpl._read()
        return tpl.num_tpl
    except Exception:
        return None


def _entry_number(display_name):
    """The archive entry number a file was unpacked under, or None.

    Entries in these containers have no names of their own, only a position,
    so albam numbers them "<archive>_NNN.<ext>" (see engines/cie/fs.py). That
    number is the only thing relating one entry to another.
    """
    stem = display_name.rsplit(".", 1)[0]
    _, _, number = stem.rpartition("_")
    return int(number) if number.isdigit() else None


def _tpl_candidates(vfs, bin_vfile):
    """Every .tpl sharing a root with `bin_vfile`."""
    root_id = bin_vfile.tree_node.root_id
    return [vf for vf in vfs.file_list
            if vf.tree_node.root_id == root_id and
            vf.display_name.lower().endswith(".tpl")]


def choose_tpl(vfs, bin_vfile, bin):
    """The .tpl a model's materials address, or None if its archive has none.

    A model does not name its .tpl. Its materials hold indices into one, and
    the archive holds many - a character archive can carry 75 of them for 120
    models - so the pairing has to be worked out.

    Three things decide it, in order:

    1. The .tpl must have enough slots for every texture index the materials
       reference. A .tpl with fewer cannot be the one, whatever else fits.
    2. Its slot count should equal the model's own num_tpl, which counts the
       slots the model addresses.
    3. Failing a tie-break on those, the nearest .tpl following the model in
       the archive wins, then the nearest before it - packing writes a model
       and then its textures.

    Measured over every mesh model in a set of character archives (2566 of
    them): this picks a .tpl with enough slots for 99.9%, and one whose count
    matches exactly for 98.1%. Taking the archive's first .tpl, which is what
    the import panel used to default to, is right for 52%.
    """
    candidates = _tpl_candidates(vfs, bin_vfile)
    if not candidates:
        return None

    needed = 0
    for material in bin.materials:
        for slot in (material.diffuse_map, material.bump_map,
                     material.opacity_map, material.custom_specular_map):
            if slot != NO_TEXTURE:
                needed = max(needed, slot + 1)
    declared = bin.header.num_tpl
    bin_number = _entry_number(bin_vfile.display_name)

    def rank(vfile):
        count = _tpl_entry_count(vfile)
        number = _entry_number(vfile.display_name)
        known = number is not None and bin_number is not None
        distance = abs(number - bin_number) if known else 1 << 16
        follows = known and number > bin_number
        return (
            0 if (count is not None and count >= needed) else 1,
            0 if count == declared else 1,
            0 if follows else 1,
            distance,
        )

    return min(candidates, key=rank)


def _resolve_tpl(vfile, bin, context):
    """The .tpl vfile to build this model's materials from.

    "Auto" is the default because a model's .tpl is not something a user can
    reasonably be expected to know: the entries have no names, only numbers.
    An explicit choice is honoured as long as it is still in the same
    archive.
    """
    vfs = context.scene.albam.vfs
    selected = context.scene.albam.import_options_bin.tpl_file_id
    if selected and selected != AUTO_TPL:
        chosen = next((vf for vf in _tpl_candidates(vfs, vfile)
                       if vf.name == selected), None)
        if chosen is not None:
            return chosen
    return choose_tpl(vfs, vfile, bin)


def _get_tpl_files_enum(self, context):
    """The .tpl choices for the selected model, "Auto" first."""
    items = [(AUTO_TPL, "Auto", "Pick the .tpl this model's own materials fit")]
    vfs = context.scene.albam.vfs
    try:
        item = vfs.file_list[vfs.file_list_selected_index]
        root_id = item.tree_node.root_id
    except (IndexError, AttributeError, RuntimeError):
        return items

    for vf in vfs.file_list:
        if vf.display_name.lower().endswith('.tpl') and vf.tree_node.root_id == root_id:
            items.append((vf.name, vf.display_name, ""))
    return items


def filter_armatures(self, obj):
    # TODO: filter by custom properties that indicate is
    # a RE5 compatible armature
    return obj.type == 'ARMATURE'


@blender_registry.register_blender_prop_albam(name='import_options_bin')
class ImportOptionsBIN(bpy.types.PropertyGroup):
    tpl_file_id: bpy.props.EnumProperty(
        items=_get_tpl_files_enum,
        description="Which .tpl the model's textures come from. Auto works it "
                    "out from the model's own materials",
    )
    # An override. Left empty, import reuses an armature already brought in
    # from the same archive that covers this model's bones - see
    # _find_reusable_armature.
    shared_armature: bpy.props.PointerProperty(
        name="Armature", type=bpy.types.Object, poll=filter_armatures)  # noqa: F821

    def get_tpl_file(self, context):
        """Get the selected .tpl VirtualFile object"""
        vfs = context.scene.albam.vfs
        try:
            return vfs.file_list[self.tpl_file_id]
        except (KeyError, RuntimeError):
            return None


@blender_registry.register_import_options_custom_draw_func(extension='bin')
def draw_bin_options(panel_instance, context):
    panel_instance.bl_label = "BIN Options"
    layout = panel_instance.layout
    options = context.scene.albam.import_options_bin
    layout.label(text="Textures")
    layout.prop(options, 'tpl_file_id', text="")
    layout.label(text="Attach to armature (optional)")
    layout.prop(options, 'shared_armature', text="")


@blender_registry.register_import_options_custom_poll_func(extension='bin')
def poll_bin_options(panel_instance, context):
    return True


@blender_registry.register_import_operator_poll_func(extension='bin')
def poll_import_operator_for_bin(panel_class, context):
    # Import is always available: with "Auto" there is nothing for the user
    # to choose first, and a model whose archive has no .tpl at all still
    # imports, just without textures.
    return True


def _align(size, alignment=16):
    """`size` rounded up to `alignment`."""
    return (size + alignment - 1) // alignment * alignment


def _classify_mesh_ob(bl_mesh_ob):
    """
    As RE4UHD .bin files can have full or partial armature, we need to classify the mesh
    object to determine how to handle it.
    """
    if bl_mesh_ob:
        parent = bl_mesh_ob.parent
        armature_mod = bl_mesh_ob.modifiers.get("Armature")
        armature = armature_mod.object if armature_mod else None
        bin_type = None
        if parent and parent.type == 'ARMATURE':
            bin_type = 'full armature'
        elif parent and parent.type == 'EMPTY' and armature_mod:
            bin_type = 'inherited armature'
        else:
            bin_type = 'static'  # not sure if it exist
        return bin_type, armature


def _bone_id(bl_bone, fallback):
    """The .bin bone id a Blender bone stands for.

    Import names each bone after its id (see _build_armature), so the name is
    the id coming back. A bone the user added by hand won't be named that way;
    it gets its position in the armature instead, which at least stays inside
    the u1 the format allows.
    """
    name = bl_bone.name
    if name.isdigit() and int(name) < 255:
        return int(name)
    return min(fallback, 254)


def _serialize_bones(dst_bin, bl_armature):
    """The bone table, as local offsets from each bone's parent.

    The file stores a parent-relative offset per bone, while Blender holds
    absolute rest positions, so each one is differenced against its parent on
    the way out. Parent 0xFF means "no parent".
    """
    bones = list(bl_armature.data.bones)
    ids = {bone.name: _bone_id(bone, i) for i, bone in enumerate(bones)}

    dst_bones = []
    for i, bone in enumerate(bones):
        dst_bone = dst_bin.Bone(_parent=dst_bin, _root=dst_bin._root)
        dst_bone.bone_id = ids[bone.name]
        dst_bone.parent = ids[bone.parent.name] if bone.parent else NO_PARENT
        head = bone.head_local
        if bone.parent:
            head = head - bone.parent.head_local
        dst_bone.x, dst_bone.y, dst_bone.z = _zy_flip(head.x, head.y, head.z)
        dst_bone.filler = 0
        dst_bone._check()
        dst_bones.append(dst_bone)
    return dst_bones


def _weight_key(bl_mesh_ob, vertex, group_ids):
    """(bone ids, weights) for one vertex, as the format stores them.

    Weights are percentages of 100, not fractions of 255, and at most three
    bones influence a vertex. The largest three win, and the remainder is
    folded into the biggest so they sum to 100 exactly - the game reads them
    as whole percent, so anything left over is simply lost influence.
    """
    influences = []
    for group in vertex.groups:
        bone_id = group_ids.get(group.group)
        if bone_id is None or group.weight <= 0:
            continue
        influences.append((group.weight, bone_id))
    if not influences:
        return (0, 0, 0), (0, 0, 0), 0

    influences.sort(reverse=True)
    influences = influences[:MAX_BONE_INFLUENCES]
    total = sum(weight for weight, _ in influences)
    percents = [max(1, round(weight / total * 100)) for weight, _ in influences]
    percents[0] += 100 - sum(percents)
    if percents[0] < 1:
        # Three near-equal influences can push the first below 1 after the
        # others are floored up; give the largest share back to it.
        percents = [100 - (len(percents) - 1)] + [1] * (len(percents) - 1)

    bone_ids = [bone_id for _, bone_id in influences]
    while len(bone_ids) < 3:
        bone_ids.append(0)
        percents.append(0)
    return tuple(bone_ids), tuple(percents), len(influences)


def _collect_geometry(bl_mesh_objs):
    """Everything per-corner the format needs, in the order it stores it.

    The format is non-indexed: positions, normals, UVs and weight indices are
    all one entry per face corner, consumed sequentially by each material's
    strips, with no vertex sharing at all. That means no index buffer to
    build and no vertex welding to undo - a triangle is simply three more
    entries on the end of every array.

    Returns (groups, positions, normals, uvs, weight_indices, weight_table),
    where `groups` is one (bl_material, triangle count) per material in the
    order their corners appear.
    """
    groups = []
    positions = []
    normals = []
    uvs = []
    weight_indices = []
    weight_table = []
    weight_lookup = {}

    for bl_mesh_ob in bl_mesh_objs:
        bl_mesh = bl_mesh_ob.data
        armature_modifier = bl_mesh_ob.modifiers.get("Armature")
        armature = armature_modifier.object if armature_modifier else None
        group_ids = {}
        if armature:
            bone_ids = {bone.name: _bone_id(bone, i)
                        for i, bone in enumerate(armature.data.bones)}
            for group in bl_mesh_ob.vertex_groups:
                if group.name in bone_ids:
                    group_ids[group.index] = bone_ids[group.name]
                elif group.name.isdigit():
                    group_ids[group.index] = int(group.name)

        uv_layer = bl_mesh.uv_layers.active
        slots = bl_mesh_ob.material_slots

        # Polygons grouped by material slot, so each material's corners are
        # contiguous - the strips can only address them that way.
        by_material = {}
        for polygon in bl_mesh.polygons:
            by_material.setdefault(polygon.material_index, []).append(polygon)

        for material_index in sorted(by_material):
            bl_material = (slots[material_index].material
                           if material_index < len(slots) else None)
            triangles = 0
            for polygon in by_material[material_index]:
                loops = list(polygon.loop_indices)
                # Fan-triangulate: an n-gon becomes n-2 triangles sharing its
                # first corner. Nothing here needs a better triangulation -
                # the corners are written out independently either way.
                for i in range(1, len(loops) - 1):
                    for loop_index in (loops[0], loops[i], loops[i + 1]):
                        loop = bl_mesh.loops[loop_index]
                        vertex = bl_mesh.vertices[loop.vertex_index]
                        positions.append(_zy_flip(*vertex.co))
                        normals.append(loop.normal)
                        if uv_layer:
                            u, v = uv_layer.data[loop_index].uv
                        else:
                            u, v = 0.0, 0.0
                        uvs.append((u, 1.0 - v))  # V is flipped on import

                        key = _weight_key(bl_mesh_ob, vertex, group_ids)
                        index = weight_lookup.get(key)
                        if index is None:
                            index = len(weight_table)
                            weight_lookup[key] = index
                            weight_table.append(key)
                        weight_indices.append(index)
                    triangles += 1
            if triangles:
                groups.append((bl_material, triangles))

    return groups, positions, normals, uvs, weight_indices, weight_table


def _texture_slot(bl_material, input_name, app_id):
    """The .tpl slot the image wired into `input_name` came from, or 0xFF.

    A material's texture references are bindings, not values, so they live in
    the node tree rather than in the material's custom properties - which is
    also what makes swapping a texture in Blender an edit export can see.
    Import records which .tpl slot each image came from on the image itself;
    this reads it back.
    """
    if not bl_material.use_nodes:
        return NO_TEXTURE
    for node in bl_material.node_tree.nodes:
        if node.type != "GROUP" or input_name not in node.inputs:
            continue
        for link in node.inputs[input_name].links:
            image = getattr(link.from_node, "image", None)
            if image is None:
                continue
            custom_properties = image.albam_custom_properties.get_custom_properties_for_appid(
                app_id)
            index = custom_properties.tpl_index
            return index if 0 <= index < NO_TEXTURE else NO_TEXTURE
    return NO_TEXTURE


def _serialize_material(dst_bin, bl_material, triangles, app_id):
    """One material plus the face-index block that follows it inline.

    Every triangle is emitted as its own entry in a triangle-list strip
    (ftype 5), rather than as strips: the corners are already written out
    per triangle, so a list costs nothing to build and cannot get the winding
    wrong the way a mis-stitched strip can. fcount is a u2, so a material
    with more triangles than fit is split across several strips.
    """
    dst_material = dst_bin.Material(_parent=dst_bin, _root=dst_bin._root)
    for attribute in _MATERIAL_BYTE_FIELDS:
        setattr(dst_material, attribute, 0)
    for attribute in _MATERIAL_NO_TEXTURE_FIELDS:
        setattr(dst_material, attribute, NO_TEXTURE)

    if bl_material is not None:
        custom_properties = bl_material.albam_custom_properties.get_custom_properties_for_appid(
            app_id)
        custom_properties.copy_custom_properties_to(dst_material)
        for field, input_name in _TEXTURE_SLOT_INPUTS:
            setattr(dst_material, field, _texture_slot(bl_material, input_name, app_id))

    dst_face_index = dst_bin.FaceIndex(_parent=dst_material, _root=dst_bin._root)
    strips = []
    remaining = triangles
    while remaining:
        in_strip = min(remaining, MAX_TRIANGLES_PER_STRIP)
        strip = dst_bin.Strip(_parent=dst_face_index, _root=dst_bin._root)
        strip.ftype = FTYPE_TRIANGLE_LIST
        strip.fcount = in_strip * 3
        strip._check()
        strips.append(strip)
        remaining -= in_strip

    dst_face_index.strip_count = len(strips)
    dst_face_index.strips = strips
    dst_face_index.num_triangles = triangles
    # buffer_size is measured from the strip_count word and padded to 16.
    body_size = 4 + len(strips) * 4
    dst_face_index.buffer_size = _align(body_size)
    dst_face_index.padding = b"\x00" * (dst_face_index.buffer_size - body_size)
    dst_face_index._check()

    dst_material.face_index = dst_face_index
    dst_material._check()
    return dst_material


@blender_registry.register_export_function(app_id="re4uhd", extension="bin")
def export_bin(bl_obj):
    """Serialize a Blender object back to a mesh .bin.

    Everything written comes from what is in Blender now - geometry, normals,
    UVs, the armature and its weights - so an edit made there is what lands in
    the file. The handful of header words Blender has nowhere to keep (build
    stamps, the morph divisor, the TPL slot count) are carried on the mesh's
    own albam custom properties, put there at import time.
    """
    asset = bl_obj.albam_asset
    app_id = asset.app_id

    bl_mesh_objs = [bl_obj] if bl_obj.type == "MESH" else [
        child for child in bl_obj.children_recursive if child.type == "MESH"]
    if not bl_mesh_objs:
        raise AlbamCheckFailure(
            f"{bl_obj.name} has no mesh to export",
            details="A RE4 UHD model is exported from a mesh object, or from an "
                    "armature or empty with mesh children",
            solution="Select the imported model's armature, or its mesh",
        )

    _, armature = _classify_mesh_ob(bl_mesh_objs[0])
    if armature is None and bl_obj.type == "ARMATURE":
        armature = bl_obj

    (groups, positions, normals, uvs,
     weight_indices, weight_table) = _collect_geometry(bl_mesh_objs)

    num_vertices = len(positions)
    if num_vertices > MAX_VERTICES:
        raise AlbamCheckFailure(
            f"{bl_obj.name} has too much geometry to export: {num_vertices} face "
            f"corners, and the format counts them in 16 bits",
            details=f"The limit is {MAX_VERTICES}. Every triangle contributes three "
                    f"corners, since the format shares no vertices between faces.",
            solution="Reduce the polygon count, or split the model across several meshes",
        )

    dst_bin = Re4UhdBin()
    dst_bin.header = _serialize_header(dst_bin, bl_mesh_objs[0])
    dst_bin.bones = _serialize_bones(dst_bin, armature) if armature else []
    dst_bin.weights = _serialize_weights(dst_bin, weight_table)
    dst_bin.vertex_positions = _serialize_vec3s(dst_bin, positions)
    dst_bin.normals = _serialize_normals(dst_bin, normals)
    dst_bin.texcoords = _serialize_uvs(dst_bin, uvs)
    dst_bin.indexes = list(weight_indices)
    dst_bin.indexes2 = list(weight_indices)
    dst_bin.vertex_colors = _serialize_colors(dst_bin, num_vertices)
    dst_bin.materials = [_serialize_material(dst_bin, bl_material, triangles, app_id)
                         for bl_material, triangles in groups]
    # Morphs, bone pairs and adjacency are left out: their offsets stay 0 and
    # the header flags announcing them are cleared with them, which is how a
    # shipped model without them looks. They are not assigned at all rather
    # than assigned None - these are conditional Kaitai instances, and the
    # generated writer walks whatever is set.

    data_bytes = _layout_and_write(dst_bin, num_vertices)
    return [VirtualFileData(app_id, asset.relative_path, data_bytes=data_bytes)]


def _serialize_header(dst_bin, bl_mesh_ob):
    """The header, with counts and offsets left at 0 for _layout_and_write."""
    header = dst_bin.UhdBinHeader(_parent=dst_bin, _root=dst_bin._root)
    for attribute in ("offset_bones", "unk_00", "unk_01", "offset_vertex_colors",
                      "offset_vertex_texcoord", "offset_weights", "num_weights",
                      "num_bones", "num_materials", "offset_materials",
                      "texture1_flags", "texture2_flags", "num_tpl", "vertex_scale",
                      "unk_02", "num_weights2", "offset_morphs",
                      "offset_vertex_position", "offset_vertex_normals",
                      "num_vertices", "num_vertex_normals", "version_flags",
                      "offset_bonepairs", "offset_adjacents", "offset_index_buffer",
                      "offset_index_buffer2"):
        setattr(header, attribute, 0)

    custom_properties = bl_mesh_ob.data.albam_custom_properties.get_custom_properties_for_appid(
        "re4uhd")
    header.vertex_scale = custom_properties.vertex_scale
    header.num_tpl = custom_properties.num_tpl
    return header


def _serialize_weights(dst_bin, weight_table):
    dst_weights = []
    for bone_ids, percents, count in weight_table:
        dst_weight = dst_bin.FmtbinWeight(_parent=dst_bin, _root=dst_bin._root)
        dst_weight.bone_ids = list(bone_ids)
        dst_weight.weights = list(percents)
        dst_weight.count = count
        dst_weight.unk00 = 0
        dst_weight._check()
        dst_weights.append(dst_weight)
    return dst_weights


def _serialize_vec3s(dst_bin, vectors):
    dst_vectors = []
    for x, y, z in vectors:
        dst_vector = dst_bin.Vec3(_parent=dst_bin, _root=dst_bin._root)
        dst_vector.x, dst_vector.y, dst_vector.z = x, y, z
        dst_vector._check()
        dst_vectors.append(dst_vector)
    return dst_vectors


def _serialize_normals(dst_bin, normals):
    """Normals, scaled the way the shipped files carry them.

    They are unit vectors multiplied by a large constant - measured at about
    5.42e11 across real models, matching GLOBAL_NORMAL_FIX_EXTENDED. Import
    divides by the vector's own length so the scale doesn't matter coming in,
    but the game is handed these directly, so they go out at the scale it
    ships.
    """
    dst_normals = []
    for normal in normals:
        dst_normal = dst_bin.Vec3(_parent=dst_bin, _root=dst_bin._root)
        _encode_normal(dst_normal, normal, extended=True)
        dst_normal._check()
        dst_normals.append(dst_normal)
    return dst_normals


def _serialize_uvs(dst_bin, uvs):
    dst_uvs = []
    for u, v in uvs:
        dst_uv = dst_bin.Uv(_parent=dst_bin, _root=dst_bin._root)
        dst_uv.u, dst_uv.v = u, v
        dst_uv._check()
        dst_uvs.append(dst_uv)
    return dst_uvs


def _serialize_colors(dst_bin, count):
    """A white vertex-colour entry per corner.

    Every shipped model has a non-zero colour offset even though none of them
    sets the flag that says the colours are used, so the block is written to
    keep the layout shipped files have rather than for anything to read.
    """
    dst_colors = []
    for _ in range(count):
        dst_color = dst_bin.Rgba(_parent=dst_bin, _root=dst_bin._root)
        dst_color.a = dst_color.r = dst_color.g = dst_color.b = 255
        dst_color._check()
        dst_colors.append(dst_color)
    return dst_colors


def _layout_and_write(dst_bin, num_vertices):
    """Place every block, fill in the header, and serialize.

    Offsets are all explicit in the header, so the file's layout is ours to
    choose rather than something to reproduce; blocks go in the order shipped
    files use them, each aligned to 16. The header is a fixed 0x60 here - the
    format allows 0x40 and 0x50 too, which simply stop before the four
    trailing offsets, and writing the largest means never having to decide.
    """
    header = dst_bin.header
    header.num_bones = len(dst_bin.bones)
    header.num_materials = len(dst_bin.materials)
    header.num_vertices = num_vertices
    header.num_vertex_normals = num_vertices

    weight_count = len(dst_bin.weights)
    # num_weights is the u1 count the game reads while it fits; num_weights2
    # is the u2 that takes over past 255.
    header.num_weights = weight_count if weight_count <= 255 else weight_count & 0xFF
    header.num_weights2 = weight_count

    # Bit 0x80000000 is what marks the file as a mesh at all; the other two
    # say the bonepair and adjacency blocks are present, and nothing rebuilds
    # those yet. The flags word is one u4 that the .ksy still splits in two.
    flags = BIN_FLAG_IS_MESH
    header.texture1_flags = flags & 0xFFFF
    header.texture2_flags = (flags >> 16) & 0xFFFF
    header.version_flags = VERSION_FLAGS_PLAIN
    header.unk_01 = 0

    offset = HEADER_SIZE
    header.offset_bones = HEADER_SIZE
    offset = _align(offset + len(dst_bin.bones) * BONE_SIZE)

    header.offset_weights = offset if dst_bin.weights else 0
    offset = _align(offset + weight_count * WEIGHT_SIZE)

    header.offset_vertex_position = offset
    offset = _align(offset + num_vertices * VEC3_SIZE)

    header.offset_index_buffer = offset
    offset = _align(offset + num_vertices * INDEX_SIZE)

    header.offset_vertex_normals = offset
    offset = _align(offset + num_vertices * VEC3_SIZE)

    header.offset_index_buffer2 = offset
    offset = _align(offset + num_vertices * INDEX_SIZE)

    header.offset_vertex_colors = offset
    offset = _align(offset + num_vertices * RGBA_SIZE)

    header.offset_vertex_texcoord = offset
    offset = _align(offset + num_vertices * UV_SIZE)

    header.offset_materials = offset
    for dst_material in dst_bin.materials:
        offset += MATERIAL_SIZE + 8 + dst_material.face_index.buffer_size
    total_size = _align(offset)

    header._check()
    dst_bin._check()
    stream = KaitaiStream(BytesIO(bytearray(total_size)))
    dst_bin._write(stream)
    return stream.to_byte_array()
