import bpy
from ...registry import blender_registry
from .structs.tpl import Tpl


def _process_tpls(tpl_id):
    # Process TPLs in a scope of the container with BIN file
    vf_list = bpy.context.scene.albam.vfs.file_list
    tpl_vfiles = [vf for vf in vf_list if vf.name == tpl_id]
    tpl_db = []
    try:
        tpl_vfile = tpl_vfiles[0]
    except IndexError:
        raise(f"{tpl_id} wasn't found")
    
    print(f"TPL is: {tpl_vfile.display_name}")
    tpl_bytes = tpl_vfile.get_bytes()
    tpl = Tpl.from_bytes(tpl_bytes)
    tpl._read()

    try:
        tpl.tpl_entries
    except EOFError:
        print(f"The {tpl_vfile.display_name} is incorrect")

    for i, te in enumerate(tpl.tpl_entries):
        tpl_entry = {
            "tpl_name": tpl_vfile.display_name,
            "tpl_entry": te,
            "pack_name": f"{te.image_data.ids.pack_id:08x}",
            "pack_name_vfile": "",
            "texture_id": te.image_data.ids.texture_id,
            "width": te.image_data.width,
            "height": te.image_data.height,
            "vfile": None
        }

        tpl_db.append(tpl_entry)
        # print(f"Texture size: {te.image_data.width}x{te.image_data.height}")
        # print("Pack: {}, Texture ID: {} ".format(tpl_entry["pack_name"], tpl_entry["texture_id"]))
    return _process_tex_indices(tpl_db)


def _process_tex_indices(tpl_db):
    vfile_list = bpy.context.scene.albam.vfs.file_list
    cached_packs = {}
    for tp in tpl_db:
        pack_found = False
        pack_name = tp["pack_name"]
        if pack_name not in cached_packs.keys():
            for vfile in vfile_list:
                if vfile.display_name not in cached_packs.keys():
                    # there are cases when it's "0" + pack_name
                    if pack_name in vfile.display_name and vfile.is_root:
                        print(f"Found {vfile.display_name}!")
                        tp["pack_name_vfile"] = vfile.display_name
                        pack_found = True
                        cached_packs[vfile.display_name] = vfile.name
                else:
                    pack_found = True
                    tp["pack_name_vfile"] = vfile.display_name
        if not pack_found:
            print(f"{pack_name} texture pack wasn't found in the virtual file system")

    if not cached_packs:
        return None

    tex_db = {}
    for pack_name, root_id in cached_packs.items():
        tex_list = []
        for vfile in vfile_list:
            if vfile.tree_node.root_id == root_id:
                tex_list.append(vfile)
        tex_db[pack_name] = tex_list

    for tp in tpl_db:
        tex_pack = tex_db.get(tp["pack_name_vfile"], [None])
        try:
            tp["vfile"] = tex_pack[tp["texture_id"]]
        except IndexError:
            raise RuntimeError("Index {} isn't correct".format(tp["texture_id"]))
    return tpl_db


def _create_blender_image_from_tex(tpl):
    app_id = "re4uhd"
    vfile = tpl["vfile"]
    bl_image = bpy.data.images.get(vfile.display_name)
    if bl_image:
        return bl_image

    tex = vfile.get_bytes()

    bl_image = bpy.data.images.new(f"{vfile.display_name}", tpl["width"], tpl["height"])
    bl_image.source = "FILE"
    bl_image.pack(data=tex, data_len=len(tex))

    bl_image.albam_asset.app_id = app_id
    custom_properties = bl_image.albam_custom_properties.get_custom_properties_for_appid(app_id)
    custom_properties.tpl_id = tpl["tpl_name"]
    custom_properties.pack_id = tpl["pack_name"]
    image_data = tpl["tpl_entry"].image_data
    custom_properties.set_from_source(image_data)
    return bl_image


@blender_registry.register_custom_properties_image("tex_cie", ("re4uhd",))
@blender_registry.register_blender_prop
class TexCIECustomProperties(bpy.types.PropertyGroup):
    tpl_id: bpy.props.StringProperty(default="")
    pack_id: bpy.props.StringProperty(default="")
    pixel_format_type: bpy.props.IntProperty(default=0)
    id_offset: bpy.props.IntProperty(default=0)
    wrap_s: bpy.props.IntProperty(default=0)
    wrap_t: bpy.props.IntProperty(default=0)
    min_filter: bpy.props.IntProperty(default=0)
    mag_filter: bpy.props.IntProperty(default=0)
    lod_bias: bpy.props.FloatProperty(default=0.0)
    enable_lod: bpy.props.IntProperty(default=0)
    min_lod: bpy.props.IntProperty(default=0)
    max_lod: bpy.props.IntProperty(default=0)
    is_compressed: bpy.props.IntProperty(default=0)


    # XXX copy paste in mesh, material
    def set_from_source(self, mesh):
        # XXX assume only properties are part of annotations
        for attr_name in self.__annotations__:
            self.copy_attr(mesh, self, attr_name)

    def set_to_dest(self, mesh):
        for attr_name in self.__annotations__:
            self.copy_attr(self, mesh, attr_name)

    @staticmethod
    def copy_attr(src, dst, name):
        # will raise, making sure there's consistency
        try:
            src_value = getattr(src, name)
            setattr(dst, name, src_value)
        except AttributeError:
            print(name)

        #try:
        #    if isinstance(src_value, str):
        #        src_value = int(src_value, 16)
        #    setattr(dst, name, src_value)
        #except TypeError:
        #    setattr(dst, name, hex(src_value))
