import bpy
import bmesh
from mathutils import Matrix


def unselect():
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except RuntimeError:
        pass
    for ob in bpy.context.selected_objects:
        # ob.select = False
        ob.select_set(False)
    bpy.ops.object.select_all(action='DESELECT')
    return


def apply_transform(objects):
    unselect()
    for obj in objects:  # bpy.context.scene.objects:
        obj.select_set(obj.type == "MESH")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action='DESELECT')


def create_root_nub(name):
    ob = bpy.data.objects.new(name, None)
    # bpy.context.collection.objects.link(ob)  # pytest screams it's re-add
    ob.matrix_local = Matrix.Identity(4)
    ob.show_wire = True
    ob.show_in_front = True
    return ob


def delete_ob(obj):
    objs = bpy.data.objects
    objs.remove(objs[obj.name], do_unlink=True)


def get_blender_objects(blenderType=None, key=None):
    checks = []
    if blenderType is not None:
        checks.append(lambda x: x.type == blenderType)
    if key is not None:
        checks.append(lambda x: "Type" in x and key in x["Type"])
    return [obj for obj in bpy.context.scene.objects if all((c(obj) for c in checks))]


def get_meshes(key=None):
    return get_blender_objects("MESH", key)


def get_empties(key=None):
    return get_blender_objects("EMPTY", key)


def clone_mesh(original, keep_modifiers=False):
    copy = original.copy()
    bpy.context.collection.objects.link(copy)
    bpy.context.view_layer.objects.active = copy
    original.select_set(False)
    copy.select_set(True)
    bpy.ops.object.make_single_user(
        type='SELECTED_OBJECTS', object=True, obdata=True)
    copy.data.transform(copy.matrix_world)

    copy.matrix_world = Matrix()
    if not keep_modifiers:
        for mod in copy.modifiers:
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except RuntimeError:
                pass
    return copy


def join_mesh(source, target, doUpdate=True, translate=[0.0, 0.0, 0.0], alignTo=None):
    bm = bmesh.new()
    bm.from_mesh(source.data)
    bm.from_mesh(target.data)
    bm.to_mesh(target.data)
    # target.data.update()
    delete_ob(source)
    return target

    result = False
    # Check that the passed objects exist and are mesh objects.
    if target is not None and target.type == 'MESH' and source is not None and source.type == 'MESH':
        # Get the source and target mesh data, applying any modifiers to the source.
        # TODO: Should we get this in some other way?
        scene = bpy.context.scene
        sourceMesh = source.to_mesh(scene, True, 'PREVIEW')
        targetMesh = target.data
        # VERTICES #
        numVertices = copy_vertices(sourceMesh, targetMesh, translate, alignTo)
        # MATERIALS #
        materialsMap = copy_materials(sourceMesh, targetMesh)
        # FACES #
        copy_faces(sourceMesh, targetMesh, numVertices, materialsMap)
        if doUpdate is True:
            targetMesh.update(calc_edges=True)
        result = True
        delete_ob(source)
    return result


def copy_vertices(sourceMesh, targetMesh, translate, alignTo):
    numVertices = len(targetMesh.vertices)
    numAppendVertices = len(sourceMesh.vertices)
    targetMesh.vertices.add(numAppendVertices)
    for v in range(numAppendVertices):
        # Transform the vertex coordinates into that of the new object.
        newLocation = sourceMesh.vertices[v].co
        # Apply align/translate transformations.
        if alignTo is not None:
            quat = alignTo.to_track_quat('-Y', 'Z')
            mat = quat.to_matrix().to_4x4()
            mat[3][0:3] = translate
            newLocation = mat * newLocation
        targetMesh.vertices[numVertices + v].co = newLocation
    return numVertices


def copy_materials(sourceMesh, targetMesh):
    # We need maintain a map between our source and target materials as we'll be merging, not
    # simply appending like we do with the vertices and faces.
    materialsMap = {}
    # Link any materials to the target that are linked to the source (without duplicating links).
    # Then, when we bring over the faces we'll also bring over the material assignments.
    for sourceMaterialIndex in range(len(sourceMesh.materials)):
        sourceMaterial = sourceMesh.materials[sourceMaterialIndex]
        targetHasMaterial = False
        for targetMaterialIndex in range(len(targetMesh.materials)):
            targetMaterial = targetMesh.materials[targetMaterialIndex]
            if sourceMaterial.name == targetMaterial.name:
                targetHasMaterial = True
                materialsMap[sourceMaterialIndex] = targetMaterialIndex
                break

        if not targetHasMaterial:
            materialsMap[sourceMaterialIndex] = len(targetMesh.materials)
            targetMesh.materials.append(sourceMaterial)
    return materialsMap


def copy_faces(sourceMesh, targetMesh, numVertices, materialsMap):
    numFaces = len(targetMesh.polygons)
    numAppendFaces = len(sourceMesh.polygons)
    targetMesh.polygons .add(numAppendFaces)
    for sourceFaceIndex in range(numAppendFaces):
        sourceFace = sourceMesh.polygons[sourceFaceIndex]
        targetFace = targetMesh.polygons[sourceFaceIndex + numFaces]
        x_fv = sourceFace.vertices
        o_fv = [i + numVertices for i in x_fv]
        # However, we need to offset the index by the number of faces in the host mesh we are appending to.
        if len(x_fv) == 4:
            targetFace.vertices_raw = o_fv
        else:
            targetFace.vertices = o_fv
        # Copy the face smooth and material assignments (only if there are materials to assign).
        targetFace.use_smooth = sourceFace.use_smooth
        if (len(materialsMap) > 0):
            targetFace.material_index = materialsMap[sourceFace.material_index]


def triangulate_meshes(bl_objects):
    for ob in bl_objects:
        mesh = ob.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
        bm.to_mesh(mesh)
        mesh.update()


def move_to_collection(bl_objects, col_name):
    collection = bpy.data.collections.get(col_name)
    if not collection:
        collection = bpy.data.collections.new(col_name)
        # Link the collection to the scene
        bpy.context.scene.collection.children.link(collection)
    for ob in bl_objects:
        for col in ob.users_collection:
            col.objects.unlink(ob)
        collection.objects.link(ob)


def split_mesh_by_material(src_obj):
    """Split mesh by materials, preserving attributes"""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = src_obj.evaluated_get(depsgraph)
    src_mesh = eval_obj.to_mesh()

    mat_count = len(src_obj.data.materials)
    if mat_count == 0:
        eval_obj.to_mesh_clear()
        return []
    result_objects = []

    for mat_index in range(mat_count):
        dst_mesh = bpy.data.meshes.new(f"{src_obj.name}_mat{mat_index}")

        verts_map = {}  # src mesh vertex index: dst mesh vertex index
        verts_list = []
        new_faces = []

        for src_poly in src_mesh.polygons:
            if src_poly.material_index == mat_index:
                face_verts = []
                for v_idx in src_poly.vertices:
                    if v_idx not in verts_map:
                        v = src_mesh.vertices[v_idx]
                        verts_map[v_idx] = len(verts_list)
                        verts_list.append(v.co)
                    face_verts.append(verts_map[v_idx])
                new_faces.append(face_verts)

        dst_mesh.from_pydata(verts_list, [], new_faces)
        dst_mesh.update()

        # uv layers
        for uv_layer_idx, uv_layer in enumerate(src_mesh.uv_layers):
            uv_layer_new = dst_mesh.uv_layers.new(name=uv_layer.name)

            # find the corresponding dst polygon for each src polygon and copy uv data
            dst_poly_idx = 0
            for src_poly_idx, src_poly in enumerate(src_mesh.polygons):
                if src_poly.material_index == mat_index:
                    new_poly = dst_mesh.polygons[dst_poly_idx]

                    for loop_offset in range(len(src_poly.loop_indices)):
                        old_loop_idx = src_poly.loop_indices[loop_offset]
                        new_loop_idx = new_poly.loop_indices[loop_offset]
                        uv_layer_new.data[new_loop_idx].uv = uv_layer.data[old_loop_idx].uv
                    dst_poly_idx += 1

        # vertex colors
        for col_attr in src_mesh.color_attributes:
            new_col = dst_mesh.color_attributes.new(
                name=col_attr.name,
                domain=col_attr.domain,
                type=col_attr.type
            )

            if col_attr.domain == 'POINT':
                # Vertex color
                for src_v_idx, dst_v_idx in verts_map.items():
                    new_col.data[dst_v_idx].color = col_attr.data[src_v_idx].color
            elif col_attr.domain == 'CORNER':
                # Face corner color
                dst_poly_idx = 0
                for src_poly_idx, src_poly in enumerate(src_mesh.polygons):
                    if src_poly.material_index == mat_index:
                        new_poly = dst_mesh.polygons[dst_poly_idx]
                        for loop_offset in range(len(src_poly.loop_indices)):
                            old_loop_idx = src_poly.loop_indices[loop_offset]
                            new_loop_idx = new_poly.loop_indices[loop_offset]
                            new_col.data[new_loop_idx].color = col_attr.data[old_loop_idx].color
                        dst_poly_idx += 1

        new_normals_data = []
        for src_poly_idx, src_poly in enumerate(src_mesh.polygons):
            if src_poly.material_index == mat_index:
                for loop_offset in range(len(src_poly.loop_indices)):
                    old_loop_idx = src_poly.loop_indices[loop_offset]
                    src_normal = src_mesh.loops[old_loop_idx].normal
                    new_normals_data.append(src_normal)

        if new_normals_data:
            dst_mesh.normals_split_custom_set(new_normals_data)

        # blender object
        dst_obj = bpy.data.objects.new(dst_mesh.name, dst_mesh)
        bpy.context.collection.objects.link(dst_obj)

        # vertex groups
        for vgroup in src_obj.vertex_groups:
            new_vgroup = dst_obj.vertex_groups.new(name=vgroup.name)
            for src_v_idx, dst_v_idx in verts_map.items():
                try:
                    weight = vgroup.weight(src_v_idx)
                    new_vgroup.add([dst_v_idx], weight, 'REPLACE')
                except RuntimeError:
                    pass

        # shape keys
        if src_obj.data.shape_keys:
            if not dst_mesh.shape_keys:
                dst_mesh.shape_keys_clear()

            for shape_key in src_obj.data.shape_keys.key_blocks:
                new_shape = dst_mesh.shape_keys.key_blocks.new(name=shape_key.name)
                for src_v_idx, dst_v_idx in verts_map.items():
                    new_shape.data[dst_v_idx].co = shape_key.data[src_v_idx].co

        # material
        if mat_index < len(src_obj.data.materials) and src_obj.data.materials[mat_index]:
            dst_mesh.materials.append(src_obj.data.materials[mat_index])

        for modifier in src_obj.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object:
                new_arm_modifier = dst_obj.modifiers.new(name="Armature", type='ARMATURE')
                new_arm_modifier.object = modifier.object
                break

        result_objects.append(dst_obj)

    eval_obj.to_mesh_clear()
    return result_objects
