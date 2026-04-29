import bpy
from mathutils import Vector
from ...registry import blender_registry
from ...vfs import VirtualFile
from ...lib.misc import chunks
from ...exceptions import AlbamCheckFailure
from .structs.re4_uhd_bin import Re4UhdBin
from .material import build_blender_materials


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


@blender_registry.register_import_function(app_id="re4uhd", extension="BIN", albam_asset_type="MODEL")
def build_blender_model(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    bin_bytes = vfile.get_bytes()
    bl_object_name = vfile.display_name
    _validate_bin_mesh(bin_bytes, bl_object_name)

    bin = Re4UhdBin.from_bytes(bin_bytes)
    bin._read()
    locations = [_yz_flip(v.x, v.y, v.z) for v in bin.vertex_positions]
    normals = []
    _process_normals(bin, normals)
    faces, mat_face_ranges = _build_faces(bin)

    bl_mesh = bpy.data.meshes.new(bl_object_name)
    bl_mesh.from_pydata(locations, [], faces)
    bl_mesh.update()

    # -- 4. UV coordinates --------------------------------------------------
    if bin.texcoords:
        uv_layer = bl_mesh.uv_layers.new(name="uv")
        for loop in bl_mesh.loops:
            uv = bin.texcoords[loop.vertex_index]
            uv_layer.data[loop.index].uv = (uv.u, 1.0 - uv.v)  # flip V for Blender

    # -- 5. Split normals ---------------------------------------------------
    if bin.normals:
        loop_normals = []
        for loop in bl_mesh.loops:
            n = bin.normals[loop.vertex_index]
            loop_normals.append(_yz_flip(n.x, n.y, n.z))
        bl_mesh.normals_split_custom_set(loop_normals)

    # -- 6. Per-material face assignment ------------------------------------
    _apply_materials(bl_mesh, bin, mat_face_ranges)

    # -- 7. Create mesh object ---------------------------------------------
    bl_object = bpy.data.objects.new(f"{bl_object_name}", bl_mesh)

    # -- 8. Armature + bones -----------------------------------------------
    arm_ob = _build_armature(bl_object_name, bin, context)

    if arm_ob:
        # -- 9. Vertex groups (skin weights) --------------------------------
        _apply_weights(bl_object, bin)

        bl_object.parent = arm_ob
        arm_mod = bl_object.modifiers.new("Armature", 'ARMATURE')
        arm_mod.object = arm_ob
        arm_mod.use_vertex_groups = True
        return arm_ob
    else:
        root = bpy.data.objects.new(bl_object_name, None)
        bl_object.parent = root
        return root


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


def _process_normals(bin, normals_out):
    for n in bin.normals:
        normals_out.append((n.x/16384, n.y/16384, n.z/16384))


def _apply_materials(bl_mesh, bin, mat_face_ranges):
    build_blender_materials(bl_mesh, bin)
    for mat_i, (start, end) in enumerate(mat_face_ranges):
        for fi in range(start, end):
            bl_mesh.polygons[fi].material_index = mat_i


def _find_existing_armature(bin, context):
    """
    Look for an armature in the current collection that can be reused for this BIN.

    RE4 UHD characters are split across multiple BINs (body, head, hands, etc.).
    Each BIN carries only the bones relevant to that part — a subset of the full
    skeleton. The body BIN (typically _000) imports the full armature first.
    Subsequent BINs (head, hands, etc.) need a subset of those bones, so we
    reuse the existing armature when all required bones are already present.
    """
    needed = {f"bone_{b.bone_id:03d}" for b in bin.bones}
    for obj in context.collection.objects:
        if obj.type != 'ARMATURE':
            continue
        existing = {b.name for b in obj.data.bones}
        # Reuse if all needed bones are present (subset: head/hands ⊆ full body)
        if needed.issubset(existing):
            return obj
    return None


# Bones are stored as LOCAL offsets from parent in millimeters (confirmed via debug:
# bone_000 raw_y=1140 = 1.14m hip height, bone_004 accumulated = 1.65m chest).
BONE_SCALE = 0.001  # same raw unit as vertex positions (*0.01 = Blender meters)


def _build_armature(bl_object_name, bin, context):
    """Create an armature object from BIN bones and return it, or None if no bones."""
    if not bin.bones:
        return None

    # Reuse an existing armature if the scene already has one with matching bones.
    # This avoids duplicates when importing multiple BINs from the same character.
    existing = _find_existing_armature(bin, context)
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
        local = Vector((b.x * BONE_SCALE, -b.z * BONE_SCALE, b.y * BONE_SCALE))
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

    for b in bin.bones:
        eb = arm_data.edit_bones.new(f"bone_{b.bone_id:03d}")
        head = world_positions[b.bone_id]
        eb.head = head

        children = [c for c in bin.bones
                    if c.parent == b.bone_id and c.bone_id != b.bone_id]
        if children:
            child_avg = sum((world_positions[c.bone_id] for c in children), Vector((0, 0, 0)))
            child_avg /= len(children)
            eb.tail = child_avg if (child_avg - head).length > 0.001 else head + Vector((0, 0, 0.02))
        else:
            eb.tail = head + Vector((0, 0, 0.02))

        edit_bone_map[b.bone_id] = eb

    for b in bin.bones:
        if b.parent != b.bone_id and b.parent in edit_bone_map:
            edit_bone_map[b.bone_id].parent = edit_bone_map[b.parent]
            edit_bone_map[b.bone_id].use_connect = False

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
        name = f"bone_{bone_id:03d}"
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
        if wm.count >= 1:
            active.append((wm.bone_id1, wm.weight1))
        if wm.count >= 2:
            active.append((wm.bone_id2, wm.weight2))
        if wm.count >= 3:
            active.append((wm.bone_id3, wm.weight3))

        total = sum(w for _, w in active)
        if total == 0:
            continue

        for bone_id, raw_w in active:
            get_vg(bone_id).add([vert_i], raw_w / total, 'REPLACE')

    print(f"[re4uhd] weights: {len(weight_index)} verts, {len(vg_cache)} vertex groups")

# -- Coordinate conversion ---------------------------------------------------

def _yz_flip(x, y, z):
    """Convert Y-up (RE4, milimeters) to Z-up (Blender, meters)."""
    return (x * 0.001, -z * 0.001, y * 0.001)


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


@blender_registry.register_blender_prop_albam(name='import_options_bin')
class ImportOptionsBIN(bpy.types.PropertyGroup):
    tpl_file_id: bpy.props.EnumProperty(
        items=_get_tpl_files_enum,
        description="Select .tpl file"
    )

    def get_tpl_file(self, context):
        """Get the selected .tpl VirtualFile object"""
        vfs = context.scene.albam.vfs
        try:
            return vfs.file_list[self.tpl_file_id]
        except (KeyError, RuntimeError):
            return None


@blender_registry.register_import_options_custom_draw_func(extension='BIN')
def draw_bin_options(panel_instance, context):
    panel_instance.bl_label = "BIN Options"
    layout = panel_instance.layout
    layout.prop(context.scene.albam.import_options_bin, 'tpl_file_id', text="TPL File")


@blender_registry.register_import_options_custom_poll_func(extension='BIN')
def poll_bin_options(panel_instance, context):
    return True


@blender_registry.register_import_operator_poll_func(extension='BIN')
def poll_import_operator_for_bin(panel_class, context):
    return bool(context.scene.albam.import_options_bin.tpl_file_id)
