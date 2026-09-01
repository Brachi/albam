import bpy
from ..common_op import _get_albam_mat_props


def _generate_lm_name(key, lm_mode):
    name = bpy.context.scene.albam.tools_settings.lm_name
    match lm_mode:
        case "0":
            return key + "_LM_new"
        case "1":
            return key
        case "2":
            return name
        case _:
            raise ValueError(f"Invalid lm_mode: {lm_mode}")


def _setup_vertex_colors(bl_objects):
    for bl_ob in bl_objects:
        color_attr = bl_ob.data.color_attributes
        if not color_attr:
            color_attr.new(name="vc", domain='POINT', type='BYTE_COLOR')
        else:
            color_attr[0].name = "vc"
        index = list(color_attr).index(color_attr["vc"])
        color_attr.render_color_index = index
        color_attr.active_color_index = index


def _setup_lightmaps(bl_objects, app_id):
    for bl_ob in bl_objects:
        albam_properties = _get_albam_mat_props(bl_ob, app_id)
        has_nmap = albam_properties.func_normalmap != "0x0"
        assert len(bl_ob.data.uv_layers) >= 2, f"{bl_ob.name} doesn't have lightmap uv layer"
        if has_nmap and len(bl_ob.data.uv_layers) == 2:
            _duplicate_uv_for_normal_map(bl_ob)
        _rename_uv_layers(bl_ob)


def _find_mesh_objects_by_parent(bl_objects):
    lm_objects = {}
    parent_objects = set()
    for bl_ob in bl_objects:
        parent_ob = bl_ob.parent
        if not parent_ob:
            continue
        parent_objects.add(parent_ob)
    scene_objects = [ob for ob in bpy.context.scene.objects if ob.type == 'MESH' and ob.parent is None]
    for parent_ob in parent_objects:
        for bl_ob in scene_objects:
            if bl_ob.parent == parent_ob:
                if lm_objects.get(parent_ob.name):
                    lm_objects[parent_ob.name].append(bl_ob)
                else:
                    lm_objects[parent_ob.name] = [bl_ob]
    return lm_objects


def _find_mesh_objects_by_lightmaps(bl_objects):
    lm_objects = {}
    lm_names = []
    for bl_ob in bl_objects:
        bl_mat = bl_ob.data.materials[0]
        lm = _find_and_select_lightmap(bl_mat)
        if lm:
            lm_names.append(lm.name)
    scene_objects = [ob for ob in bpy.context.scene.objects if ob.type == 'MESH' and ob.parent is not None]

    for bl_ob in scene_objects:
        for slot in bl_ob.material_slots:
            mat = slot.material
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        if node.image.name in lm_names:
                            if lm_objects.get(node.image.name):
                                lm_objects[node.image.name].append(bl_ob)
                            else:
                                lm_objects[node.image.name] = [bl_ob]
                            break
    return lm_objects


def _find_and_select_lightmap(bl_mat):
    bl_mat_nodes = bl_mat.node_tree.nodes
    image_nodes = [node for node in bl_mat_nodes if node.type == "TEX_IMAGE"]
    lm = None
    for img_node in image_nodes:
        links = img_node.outputs["Color"].links
        if not links:
            continue
        mtfw_shader_link_name = links[0].to_socket.name
        if mtfw_shader_link_name == 'Lightmap LM':
            lm = img_node.image
            bl_mat.node_tree.nodes.active = img_node
            for node in bl_mat_nodes:
                node.select = False
            bl_mat_nodes.active = img_node
            break
    return lm


def _group_lm_objects(bl_objects, lm_mode, app_id):
    lm_objects = []
    vc_objects = []
    lm_groups = {}
    for bl_ob in bl_objects:
        if not bl_ob.data.materials:
            continue
        custom_properties = _get_albam_mat_props(bl_ob, app_id)
        if custom_properties.vtype not in ("0x3", "0x2"):
            continue
        if custom_properties.func_lightmap in ("0x5", "0x6"):
            vc_objects.append(bl_ob)
        elif custom_properties.func_lightmap in ("0x1", "0x2", "0x3" "0x4"):
            lm_objects.append(bl_ob)
    match lm_mode:
        case "0":
            lm_groups = _find_mesh_objects_by_parent(bl_objects)
        case "1":
            lm_groups = _find_mesh_objects_by_lightmaps(bl_objects)
        case "2":
            lm_groups["selected"] = bl_objects
        case _:
            print(f"The lightmap mode {lm_mode} isn't correct")
    return vc_objects, lm_groups


def bake_light(bl_objects, lm_size, lm_mode, app_id):
    baked_img_cache = set()
    lm_mats = []
    vc_ob, lm_ob = _group_lm_objects(bl_objects, lm_mode, app_id)
    bpy.ops.object.select_all(action='DESELECT')

    if vc_ob:
        _setup_vertex_colors(vc_ob)
        for bl_ob in vc_ob:
            bl_ob.select_set(True)
        _render_lightmaps('VERTEX_COLORS')

    if lm_ob:
        for k, lm_objects in lm_ob.items():
            _setup_lightmaps(lm_objects, app_id)
            lmap_name = _generate_lm_name(k, lm_mode)
            for bl_ob in lm_objects:
                mat = bl_ob.data.materials[0]
                if mat not in lm_mats:
                    lm_mats.append(mat)
            for mat in lm_mats:
                baked_img_cache.add(_setup_mtfw_material(mat, lmap_name, lm_size))

    bpy.ops.object.select_all(action='DESELECT')
    if lm_mats:
        for lm_objects in lm_ob.values():
            for bl_ob in lm_objects:
                bl_ob.select_set(True)
                custom_properties = _get_albam_mat_props(bl_ob, app_id)
                uv_name = "uv2" if custom_properties.func_normalmap == "0x0" else "uv3"
                for uv in bl_ob.data.uv_layers:
                    uv.active = (uv.name == uv_name)
        _render_lightmaps()
        for bimage in baked_img_cache:
            bimage.pack()
        bpy.ops.object.select_all(action='DESELECT')
        for lm_objects in lm_ob.values():
            for bl_ob in lm_objects:
                for uv in bl_ob.data.uv_layers:
                    uv.active = (uv.name == "uv1")


def _duplicate_uv_for_normal_map(ob):
    """
    In re5 materials with enabled normal map uses third uv channel for lightmaps
    the function create copy of the second uv channel, then overwrite the original
    with the date from the first
    """
    mesh = ob.data
    mesh.uv_layers.active_index = 1
    mesh.uv_layers.new(name="new_lightmap")
    mesh.uv_layers.active_index = 0

    uv1_data = mesh.uv_layers[0].data
    uv2_data = mesh.uv_layers[1].data

    for i in range(len(uv1_data)):
        uv2_data[i].uv = uv1_data[i].uv

    for mat in ob.data.materials:
        if not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.bl_idname == "ShaderNodeUVMap":
                if node.uv_map == mesh.uv_layers[1].name:
                    node.uv_map = mesh.uv_layers[2].name


def _rename_uv_layers(ob):
    """
    Rename existing uv layer to Albam scheme (uv1, uv2, uv3, ...)
    """
    uv_layer_names = {}
    for i, uv in enumerate(ob.data.uv_layers):
        if uv.name != "uv" + str(i + 1):
            uv_layer_names[uv.name] = "uv" + str(i + 1)
        uv.name = "uv" + str(i + 1)
    # update the value in UVmap node after renaming the layer
    if uv_layer_names:
        for mat in ob.data.materials:
            if not mat.use_nodes:
                continue
            for node in mat.node_tree.nodes:
                if node.bl_idname == "ShaderNodeUVMap":
                    uv_name = uv_layer_names.get(node.uv_map)
                    if uv_name:
                        node.uv_map = uv_name


def _setup_mtfw_material(bl_mat, lmap_name='Lightmap LM', size=1024):
    bl_mat_nodes = bl_mat.node_tree.nodes
    image_nodes = [node for node in bl_mat_nodes if node.type == "TEX_IMAGE"]
    bake_image = bpy.data.images.get(lmap_name)
    if bake_image is None:
        bake_image = bpy.data.images.new(
            lmap_name,
            size,
            size,
        )
    lm_found = False
    for img_node in image_nodes:
        links = img_node.outputs["Color"].links
        if not links:
            continue
        mtfw_shader_link_name = links[0].to_socket.name
        if mtfw_shader_link_name == 'Lightmap LM':
            lm_found = True
            img_node.image = bake_image
            bl_mat.node_tree.nodes.active = img_node
            for node in bl_mat_nodes:
                node.select = False
            bl_mat_nodes.active = img_node
            break
    if not lm_found:
        shader_node_grp = bl_mat.node_tree.nodes.get("MTFrameworkGroup")
        link = bl_mat.node_tree.links.new
        uv_map_node = bl_mat.node_tree.nodes.new("ShaderNodeUVMap")
        uv_map_node.location = (-500, -700)
        uv_map_node.uv_map = "uv2"
        img_node = bl_mat.node_tree.nodes.new("ShaderNodeTexImage")
        img_node.location = (-300, -700)
        img_node.image = bake_image
        link(uv_map_node.outputs[0], img_node.inputs[0])
        link(img_node.outputs["Color"], shader_node_grp.inputs["Lightmap LM"])
        for node in bl_mat_nodes:
            node.select = False
        bl_mat_nodes.active = img_node
    return bake_image


def _render_lightmaps(mode='IMAGE_TEXTURES'):
    bake_settings = bpy.context.scene.render.bake
    bake_settings.use_pass_color = False
    bake_settings.target = mode
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.ops.object.bake(type='DIFFUSE')
