import bpy
from mathutils import Vector
import math
from ...registry import blender_registry
from ...vfs import VirtualFile
from ...lib.misc import chunks
from ...lib.blender import (triangles_list_to_vtx_strips,
                            get_uvs_per_vertex,
                            get_bone_indices_and_weights_per_vertex)
from ...lib.common_op import split_mesh_by_material, move_to_collection, delete_ob
from ...exceptions import AlbamCheckFailure
from .structs.re4_uhd_bin import Re4UhdBin
from .material import build_blender_materials


# Bones are stored as LOCAL offsets from parent in millimeters (confirmed via debug:
# bone_000 raw_y=1140 = 1.14m hip height, bone_004 accumulated = 1.65m chest).
GLOBAL_SCALE = 0.001  # same raw unit as vertex positions
GLOBAL_NORMAL_FIX_EXTENDED = 545460800000
GLOBAL_NORMAL_FIX_REDUCED = 16384

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
            details=f"The file is smaller than a minimum size {re4uhd_bin_mesh_hdr_size } bytes",
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

    _apply_materials(bl_mesh, bin, mat_face_ranges)
    bl_mesh_ob = bpy.data.objects.new(f"{bl_object_name}.000", bl_mesh)
    _build_shape_keys(bl_mesh_ob, bin)

    # usually only one armature is full, other bin files include only bones used by the mesh
    shared_armature = bpy.context.scene.albam.import_options_bin.shared_armature
    skeleton = _build_armature(bl_object_name, bin, context, shared_armature)

    if skeleton:
        _apply_weights(bl_mesh_ob, bin)
        arm_mod = bl_mesh_ob.modifiers.new("Armature", 'ARMATURE')
        arm_mod.object = skeleton
        arm_mod.use_vertex_groups = True

    if skeleton and not shared_armature:
        bl_object = skeleton
    else:
        bl_object = bpy.data.objects.new(bl_object_name, None)

    bl_mesh_ob.parent = bl_object
    return bl_object


def _yz_flip(x, y, z):
    """Convert Y-up (RE4, milimeters) to Z-up (Blender, meters)."""
    return (x * GLOBAL_SCALE, -z * GLOBAL_SCALE, y * GLOBAL_SCALE,)


def _zy_flip(x, y, z):
    """Convert Z-up (Blender, meters) to Y-up (RE4, milimeters)"""
    return (x / GLOBAL_SCALE, y / GLOBAL_SCALE, -z / GLOBAL_SCALE)  # in some cases returned as generator


def _build_shape_keys(bl_ob, bin):
    if not bin.morphs:
        return
    extra_scale = 2 ** bin.header.vertex_scale

    def _yz_flip_scaled(x, y, z):
        return ((x / extra_scale), (z / extra_scale), (y / extra_scale))
    bl_ob.shape_key_add(name="Basis", from_mix=False)

    for i, morph in enumerate(bin.morphs.groups):
        sk = bl_ob.shape_key_add(name=str(i), from_mix=False)
        for i, vtx in enumerate(morph.body.vertices):
            vtx_shift = _yz_flip_scaled(vtx.pos_x, vtx.pos_y, vtx.pos_z)
            sk.data[vtx.vertex_id].co.x += vtx_shift[0] * GLOBAL_SCALE
            sk.data[vtx.vertex_id].co.y += vtx_shift[1] * GLOBAL_SCALE
            sk.data[vtx.vertex_id].co.z += vtx_shift[2] * GLOBAL_SCALE


def _decode_normal(n):
    normal_fix = math.sqrt(n.x ** 2 + n.y ** 2 + n.z ** 2)
    if normal_fix == 0:
        normal_fix = 1
    return (n.x/normal_fix, n.z/normal_fix * -1, n.y/normal_fix)


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


def _apply_materials(bl_mesh, bin, mat_face_ranges):
    build_blender_materials(bl_mesh, bin)
    for mat_i, (start, end) in enumerate(mat_face_ranges):
        for fi in range(start, end):
            bl_mesh.polygons[fi].material_index = mat_i


def _build_armature(bl_object_name, bin, context, shared_armature=None):
    """Create an armature object from BIN bones and return it, or None if no bones."""
    if not bin.bones:
        return None

    # Reuse an existing armature if the scene already has one with matching bones.
    # This avoids duplicates when importing multiple BINs from the same character.
    existing = shared_armature
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
            blender_bone.tail = child_avg if (child_avg - head).length > 0.001 else head + Vector((0, 0, 0.02))
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

    print(f"[re4uhd] armature: {len(bin.bones)} bones")
    return arm_ob


# -- Vertex weights ----------------------------------------------------------
def _apply_weights(mesh_ob, bin):
    """
    Create vertex groups and assign bone weights.

    bin.indexes[i]  = WeightMap index for vertex i (vertex_weight_index_offset)
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


def _get_tpl_files_enum(self, context):
    """Dynamically generate enum items for available .tpl files in same root"""
    vfs = context.scene.albam.vfs
    try:
        index = vfs.file_list_selected_index
        item = vfs.file_list[index]
        root_id = item.tree_node.root_id
    except (IndexError, AttributeError, RuntimeError):
        return [("", "No files loaded", "")]

    items = []
    for vf in vfs.file_list:
        if vf.display_name.lower().endswith('.tpl') and vf.tree_node.root_id == root_id:
            items.append((vf.name, vf.display_name, ""))

    return items if items else [("", "No .tpl files found", "")]


def filter_armatures(self, obj):
    # TODO: filter by custom properties that indicate is
    # a RE5 compatible armature
    return obj.type == 'ARMATURE'


@blender_registry.register_blender_prop_albam(name='import_options_bin')
class ImportOptionsBIN(bpy.types.PropertyGroup):
    tpl_file_id: bpy.props.EnumProperty(
        items=_get_tpl_files_enum,
        description="Select .tpl file"
    )
    shared_armature: bpy.props.PointerProperty(type=bpy.types.Object, poll=filter_armatures)

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
    layout.label(text="TPL File")
    layout.prop(context.scene.albam.import_options_bin, 'tpl_file_id', text="")
    layout.label(text="Use already imported armature")
    layout.prop(context.scene.albam.import_options_bin, 'shared_armature', text="")


@blender_registry.register_import_options_custom_poll_func(extension='bin')
def poll_bin_options(panel_instance, context):
    return True


@blender_registry.register_import_operator_poll_func(extension='bin')
def poll_import_operator_for_bin(panel_class, context):
    return bool(context.scene.albam.import_options_bin.tpl_file_id)


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


def _serialize_bones(dst_bin, bones):
    dst_bones = []
    for bone in bones:
        dst_bone = dst_bin.Bone(_parent=dst_bin, _root=dst_bin._root)
        dst_bone.bone_id = int(bone.get('cie.anim_retarget', 255))
        dst_bone.parent = bone.parent
        dst_bone.x, dst_bone.y, dst_bone.z = _yz_flip(bone.head.x, bone.head.y, bone.head.z)
        dst_bone._check()
        dst_bones.append(dst_bone)
    return dst_bones


def _serialize_vertex_positions(dst_bin, vtx_locations):
    dst_vertex_positions = []
    for loc in vtx_locations:
        dst_vtx = dst_bin.Vec3(_parent=dst_bin, _root=dst_bin._root)
        locl = list(loc)  # WTF? debug says it's tuple, the error says it's generator
        dst_vtx.x = locl[0]
        dst_vtx.y = locl[1]
        dst_vtx.z = locl[2]
        dst_vtx._check()
        dst_vertex_positions.append(dst_vtx)
    return dst_vertex_positions


def _serialize_skinweights(dst_bin, vtx_weights):
    dst_skinweights = []
    for vw in vtx_weights.values():
        dst_bin_weight = dst_bin.FmtbinWeight(_parent=dst_bin, _root=dst_bin._root)
        count = 0
        for w in vw:
            dst_bin_weight.count = count
            count += 1

    return dst_skinweights


def _serialize_vertex_normals(dst_bin, vtx_normals):
    dst_vertex_normals = []
    for n in vtx_normals:
        dst_n = dst_bin.Vec3(_parent=dst_bin, _root=dst_bin._root)
        _encode_normal(dst_n, Vector(n), extended=True)
        dst_n._check()
        dst_vertex_normals.append(dst_n)
    return dst_vertex_normals


@blender_registry.register_export_function(app_id="re4uhd", extension="bin")
def export_bin(bl_obj):
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    vfiles = []
    vtx_locations = []
    vtx_normals = []
    vtx_uvs = []
    vtx_colors = []
    separated_mesh_objs = []
    materials = []

    src_bin = Re4UhdBin.from_bytes(asset.original_bytes)
    src_bin._read()
    dst_bin = Re4UhdBin()

    bl_mesh_objs = [c for c in bl_obj.children_recursive if c.type == "MESH"]
    try:
        bin_type, armature = _classify_mesh_ob(bl_mesh_objs[0])
    except IndexError:
        raise "No mesh objects found to export"
    if bpy.data.collections.get("AlbamTemp"):
        for ob in bpy.data.collections["AlbamTemp"].objects:
            delete_ob(ob)

    for bl_mesh_ob in bl_mesh_objs:
        separated_mesh_objs.extend(split_mesh_by_material(bl_mesh_ob))
    move_to_collection(separated_mesh_objs, "AlbamTemp")

    for bl_mesh_ob in separated_mesh_objs:
        vtx_skinweights = get_bone_indices_and_weights_per_vertex(bl_mesh_ob)
        bl_mat = bl_mesh_ob.material_slots[0].material if bl_mesh_ob.material_slots else None
        dst_mat = dst_bin.Material(_parent=dst_bin, _root=dst_bin._root)
        custom_properties = bl_mat.albam_custom_properties.get_custom_properties_for_appid(app_id)
        custom_properties.copy_custom_properties_to(dst_mat)

        dst_face_idx = dst_bin.FaceIndex(_parent=dst_mat, _root=dst_bin._root)
        loop_cache = {loop.vertex_index: loop for loop in bl_mesh_ob.data.loops}

        vtx_uvs.extend(get_uvs_per_vertex(bl_mesh_ob, 0))
        for vtx in bl_mesh_ob.data.vertices:
            vtx_locations.append(_zy_flip(vtx.co.x, vtx.co.y, vtx.co.z))

        strips_vtx = triangles_list_to_vtx_strips(bl_mesh_ob)
        dst_strips = []
        for strip in strips_vtx:
            vtx_locations.append(_zy_flip(vtx.co.x, vtx.co.y, vtx.co.z) for vtx in strip)
            for vtx in strip:
                loop = loop_cache[vtx.index]
                vtx_normals.append(_zy_flip(loop.normal.x, loop.normal.y, loop.normal.z))
            dst_strip = dst_bin.Strip(_parent=dst_face_idx, _root=dst_bin._root)
            match len(strip):
                case 3:
                    print("ftype = 5: triangle")
                    dst_strip.ftype = 5
                    dst_strip.fcount = 3
                case 4:
                    print("ftype = 8: quad")
                    dst_strip.ftype = 8
                    dst_strip.fcount = 4
                case _:
                    print("ftype = 6: strip")
                    dst_strip.ftype = 6
                    dst_strip.fcount = len(strip)
            dst_strips.append(dst_strip)
        dst_mat.face_index = dst_face_idx
        dst_mat._check()
        materials.append(dst_mat)
    # header
    dst_header = dst_bin.UhdBinHeader(_parent=dst_bin, _root=dst_bin._root)
    dst_header.offset_bones = src_bin.header.offset_bones
    dst_header.unk00 = src_bin.header.unk_00
    dst_header.unk01 = src_bin.header.unk_01
    dst_header.offset_vertex_colors = src_bin.header.offset_vertex_colors
    dst_header.offset_vertex_texcoord = src_bin.header.offset_vertex_texcoord
    dst_header.offset_weights = src_bin.header.offset_weights
    dst_header.num_weights = src_bin.header.num_weights
    dst_header.num_bones = src_bin.header.num_bones
    dst_header.num_materials = src_bin.header.num_materials
    dst_header.offset_materials = src_bin.header.offset_materials
    dst_header.texture1_flags = src_bin.header.texture1_flags
    dst_header.texture2_flags = src_bin.header.texture2_flags
    dst_header.num_tpl = src_bin.header.num_tpl
    dst_header.vertex_scale = src_bin.header.vertex_scale
    dst_header.unk_02 = src_bin.header.unk_02
    dst_header.num_weights2 = src_bin.header.num_weights2
    dst_header.offset_morphs = src_bin.header.offset_morphs
    dst_header.offset_vertex_position = src_bin.header.offset_vertex_position
    dst_header.offset_vertex_normals = src_bin.header.offset_vertex_normals
    dst_header.num_vertices = len(vtx_locations)
    dst_header.num_vertex_normals = src_bin.header.num_vertex_normals
    dst_header.version_flags = src_bin.header.version_flags
    dst_header.offset_bonepairs = src_bin.header.offset_bonepairs
    dst_header.offset_adjacents = src_bin.header.offset_adjacents
    dst_header.offset_index_buffer = src_bin.header.offset_index_buffer
    dst_header.offset_index_buffer2 = src_bin.header.offset_index_buffer2
    dst_header._check()
    dst_bin.header = dst_header
    # adjacent
    dst_adjacent = dst_bin.BoneAdj(_parent=dst_bin, _root=dst_bin._root)
    dst_adjacent.count = src_bin.adjacent.count
    dst_adjacent.adj = src_bin.adjacent.adj
    dst_adjacent._check()
    dst_bin.adjacent = dst_adjacent
    # bone pairs
    if getattr(src_bin, "bone_pairs"):  # looks like doesn't exist in inherited armature bins
        dst_bone_pairs = dst_bin.BonePair(_parent=dst_bin, _root=dst_bin._root)
        dst_bone_pairs.num_pair = src_bin.bone_pairs.num_pair
        dst_bone_pairs.line = [l for _, l in enumerate(src_bin.bone_pairs.line)]
        dst_bin.bone_pair = dst_bone_pairs
    # bones
    bones = []
    match bin_type:
        case 'full armature':
            bones = _serialize_bones(dst_bin, armature.data.bones)
        case 'inherited armature':
            vg_names_cache = []
            for mesh_ob in bl_mesh_objs:
                for vg in bl_mesh_ob.vertex_groups:
                    if vg.name not in vg_names_cache:
                        vg_names_cache.append(vg.name)
            for vg_name in vg_names_cache:
                if vg_name in armature.data.bones:
                    inherited_bones = armature.data.bones[vg_name]
            bones = _serialize_bones(dst_bin, inherited_bones)
    if not bin_type == 'static':
        dst_bin.bones = bones
    # indexes
    dst_bin.indexes = src_bin.indexes
    # indexes2
    dst_bin.indexes2 = src_bin.indexes2
    # materials
    dst_bin.materials = materials
    # normals
    dst_bin.normals = _serialize_vertex_normals(dst_bin, vtx_normals)
    # vertex colors
    dst_bin.vertex_colors = src_bin.vertex_colors
    # texcoords
    dst_bin.texcoords = src_bin.texcoords
    # vertex positions
    dst_bin.vertex_positions = _serialize_vertex_positions(dst_bin, vtx_locations)
    # weights
    dst_bin.weights = _serialize_skinweights(dst_bin, vtx_skinweights)
    return vfiles
