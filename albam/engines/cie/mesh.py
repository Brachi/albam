import bpy
from mathutils import Vector
from ...registry import blender_registry
from ...vfs import VirtualFile
from ...lib.misc import chunks
from ...exceptions import AlbamCheckFailure
from .structs.re4_uhd_bin import Re4UhdBin
from .textures import load_textures_for_model, _process_tpls, _create_blender_image_from_tex
from .material import _create_cie_shader


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
    bl_root_id = vfile.tree_node.root_id
    _validate_bin_mesh(bin_bytes, bl_object_name)

    bin = Re4UhdBin.from_bytes(bin_bytes)
    bin._read()
    locations = [_yz_flip(v.x, v.y, v.z) for v in bin.vertex_positions]
    normals = []
    _process_normals(bin, normals)
    faces, mat_face_ranges = _build_faces(bin)

    me = bpy.data.meshes.new(bl_object_name)
    me.from_pydata(locations, [], faces)
    me.update()

    # -- 4. UV coordinates --------------------------------------------------
    if bin.texcoords:
        uv_layer = me.uv_layers.new(name="uv")
        for loop in me.loops:
            uv = bin.texcoords[loop.vertex_index]
            uv_layer.data[loop.index].uv = (uv.u, 1.0 - uv.v)  # flip V for Blender

    # -- 5. Split normals ---------------------------------------------------
    if bin.normals:
        loop_normals = []
        for loop in me.loops:
            n = bin.normals[loop.vertex_index]
            loop_normals.append(_yz_flip(n.x, n.y, n.z))
        me.normals_split_custom_set(loop_normals)

    # -- 6. Per-material face assignment ------------------------------------
    _apply_materials(me, bin, mat_face_ranges, bl_root_id)

    # -- 7. Create mesh object ---------------------------------------------
    mesh_ob = bpy.data.objects.new(f"{bl_object_name}", me)

    # -- 8. Armature + bones -----------------------------------------------
    arm_ob = _build_armature(bl_object_name, bin, context)

    if arm_ob:
        # -- 9. Vertex groups (skin weights) --------------------------------
        _apply_weights(mesh_ob, bin)

        mesh_ob.parent = arm_ob
        arm_mod = mesh_ob.modifiers.new("Armature", 'ARMATURE')
        arm_mod.object = arm_ob
        arm_mod.use_vertex_groups = True

        # -- 10. Textures (optional, requires .pack.lfs in same dir) ----------
        # try:
        #    load_textures_for_model(mesh_ob, bin, vfile, context)
        # except Exception as e:
        #    print(f"[re4uhd] textures: skipped ({e})")

        return arm_ob
    else:
        root = bpy.data.objects.new(bl_object_name, None)
        mesh_ob.parent = root

        try:
            load_textures_for_model(mesh_ob, bin, vfile, context)
        except Exception as e:
            print(f"[re4uhd] textures: skipped ({e})")

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


def _apply_materials(me, bin, mat_face_ranges, bin_root_id):
    for mat_i, mat in enumerate(bin.materials):
        _create_cie_shader()
        mat_name = me.name + "_" + str(mat_i).zfill(3) + "_diff" + str(mat.diffuse_map)
        blender_material = bpy.data.materials.new(name=mat_name)
        blender_material.use_nodes = True
        blender_material.blend_method = "CLIP"
        node_to_delete = None
        for node in blender_material.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                node_to_delete = node
                blender_material.node_tree.nodes.remove(node_to_delete)
                break

        shader_node_group = blender_material.node_tree.nodes.new("ShaderNodeGroup")
        shader_node_group.node_tree = bpy.data.node_groups["RE4 UHD shader"]
        shader_node_group.name = "RE4 UHD shader group"
        shader_node_group.width = 300

        for node in blender_material.node_tree.nodes:
            if node.type == 'OUTPUT_MATERIAL':
                material_output = node
                break
        material_output.location = (400, 0)

        link = blender_material.node_tree.links.new
        link(shader_node_group.outputs[0], material_output.inputs[0])

        textures_db = _process_tpls(bin, bin_root_id)
        if textures_db:
            diffuse_map = _get_texture_from_db(textures_db, mat.diffuse_map)
            bump_map = _get_texture_from_db(textures_db, mat.bump_map)
            opacity_map = _get_texture_from_db(textures_db, mat.opacity_map)
            specular_map = _get_texture_from_db(textures_db, mat.generic_specular_map)
            special_map = _get_texture_from_db(textures_db, mat.custom_specular_map)

            tex_code_mapper = {
                1: diffuse_map,
                2: bump_map,
                3: opacity_map,
                4: specular_map,
                5: special_map,
            }
            for k, tex in tex_code_mapper.items():
                if tex:
                    blender_texture_node = blender_material.node_tree.nodes.new("ShaderNodeTexImage")
                    bl_image = _create_blender_image_from_tex(tex)
                    blender_texture_node.image = bl_image
                    if k == 1:
                        link(blender_texture_node.outputs["Color"], shader_node_group.inputs["Diffuse BM"])
                        blender_texture_node.location = (-300, 350)
                    if k == 2:
                        blender_texture_node.location = (-300, 0)
                        link(blender_texture_node.outputs["Color"], shader_node_group.inputs["Normal NM"])
                        link(blender_texture_node.outputs["Alpha"], shader_node_group.inputs["Alpha NM"])
                    if k == 4:
                        link(blender_texture_node.outputs["Color"], shader_node_group.inputs["Specular MM"])
                        blender_texture_node.location = (-300, -350)
        me.materials.append(blender_material)

    for mat_i, (start, end) in enumerate(mat_face_ranges):
        for fi in range(start, end):
            me.polygons[fi].material_index = mat_i


def _get_texture_from_db(tex_db, tex_index):
    if tex_index == 255:
        return None
    return tex_db[tex_index] if 0 <= tex_index < len(tex_db) else None


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
# Vertices are in centimeters (*0.01). Both produce ~1.7m scale in Blender.
BONE_SCALE = 0.01  # same raw unit as vertex positions (*0.01 = Blender meters)


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
    arm_data.display_type = 'OCTAHEDRAL'

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
        if wm.count >= 1: active.append((wm.bone_id1, wm.weight1))
        if wm.count >= 2: active.append((wm.bone_id2, wm.weight2))
        if wm.count >= 3: active.append((wm.bone_id3, wm.weight3))

        total = sum(w for _, w in active)
        if total == 0:
            continue

        for bone_id, raw_w in active:
            get_vg(bone_id).add([vert_i], raw_w / total, 'REPLACE')

    print(f"[re4uhd] weights: {len(weight_index)} verts, {len(vg_cache)} vertex groups")

# -- Coordinate conversion ---------------------------------------------------

def _yz_flip(x, y, z):
    """Convert Y-up (RE4, centimeters) to Z-up (Blender, meters)."""
    return (x * 0.01, -z * 0.01, y * 0.01)
