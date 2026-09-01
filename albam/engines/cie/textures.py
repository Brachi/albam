import os

import bpy
from ...registry import blender_registry
from .structs.tpl import Tpl

# The content sub-folders holding texture packs, best first: this release
# ships both the original packs and higher-resolution replacements under the
# same pack id, and a .tpl entry names only the id.
TEXTURE_PACK_FOLDERS = ("ImagePackHD", "ImagePack")


def _texture_pack_archive(pack_name, model_root):
    """The .lfs holding texture pack `pack_name`, found next to the model's
    own archive on disk, or None.

    A .tpl names its textures by pack id alone (see _process_tex_indices), and
    the pack is a separate archive - so importing a model otherwise means the
    user first working out which archive an 8-hex-digit pack id refers to and
    adding it by hand. Model archives and pack folders are siblings under one
    content directory, so that directory is two levels up from the model's
    own path and a pack is named after its id.
    """
    absolute_path = model_root.absolute_path if model_root else ""
    if not absolute_path:
        return None
    content_dir = os.path.dirname(os.path.dirname(absolute_path))
    try:
        siblings = {name.lower(): name for name in os.listdir(content_dir)}
    except OSError:
        return None

    for folder in TEXTURE_PACK_FOLDERS:
        real_folder = siblings.get(folder.lower())
        if real_folder is None:
            continue
        pack_dir = os.path.join(content_dir, real_folder)
        try:
            names = sorted(os.listdir(pack_dir))
        except OSError:
            continue
        for name in names:
            low = name.lower()
            # ".lfs" only: an unpacked ".pack.yz2" sitting next to it is not
            # something the VFS has a loader for.
            if low.startswith(pack_name) and low.endswith(".lfs"):
                return os.path.join(pack_dir, name)
    return None


def _process_tpls(tpl_id):
    # Process TPLs in a scope of the container with BIN file
    vf_list = bpy.context.scene.albam.vfs.file_list
    tpl_vfiles = [vf for vf in vf_list if vf.name == tpl_id]
    tpl_db = []
    try:
        tpl_vfile = tpl_vfiles[0]
    except IndexError:
        raise RuntimeError(f"{tpl_id} wasn't found")

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
            "model_root": tpl_vfile.root_vfile,
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
    """Resolve every TPL entry to the VFS file holding its texture bytes.

    A .tpl doesn't name its textures: an entry carries a pack id and an index
    into that pack (see structs/tpl.ksy), and the pack is a separate
    "<pack_id>.pack.yz2.lfs" archive the user has to have added to the VFS
    too. Pack roots are matched by their own file name (`in`, not equality -
    some ids are written with a leading zero the tpl entry doesn't have), and
    a texture by the index LfsFS numbered it with, parsed back out of its
    name rather than taken from its position in `file_list`, which is sorted
    by name and so only coincides with the container's own numbering while a
    pack holds under 1000 textures.
    """
    vfs = bpy.context.scene.albam.vfs
    pack_roots = {}  # pack_name : root vfile
    for tp in tpl_db:
        pack_name = tp["pack_name"]
        if pack_name in pack_roots:
            continue
        root = _find_or_mount_pack(vfs, pack_name, tp["model_root"])
        if root is not None:
            pack_roots[pack_name] = root
        else:
            print(f"{pack_name} texture pack wasn't found in the virtual file system")

    if not pack_roots:
        return None

    textures_per_pack = {}  # pack_name : {texture index : vfile}
    for pack_name, root in pack_roots.items():
        textures = {}
        # Re-read the list rather than closing over one taken earlier:
        # _find_or_mount_pack may have added a root, and a Blender
        # CollectionProperty invalidates references across an add().
        for vfile in vfs.file_list:
            if vfile.tree_node.root_id != root.name or vfile.is_root:
                continue
            index = _texture_index(vfile.display_name)
            if index is not None:
                textures[index] = vfile
        textures_per_pack[pack_name] = textures

    for tp in tpl_db:
        pack_root = pack_roots.get(tp["pack_name"])
        if pack_root is None:
            continue
        tp["pack_name_vfile"] = pack_root.display_name
        try:
            tp["vfile"] = textures_per_pack[tp["pack_name"]][tp["texture_id"]]
        except KeyError:
            raise RuntimeError(
                "Texture {} not found in {}".format(tp["texture_id"], pack_root.display_name)
            )
    return tpl_db


def _find_or_mount_pack(vfs, pack_name, model_root):
    """The VFS root for texture pack `pack_name`, mounting it from disk if the
    user hasn't added it themselves.

    Matched on `in`, not equality: an archive is named after its pack id, but
    some ids appear with a leading zero the .tpl entry doesn't carry.
    """
    for vfile in vfs.file_list:
        if vfile.is_root and pack_name in vfile.display_name:
            return vfile

    archive_path = _texture_pack_archive(pack_name, model_root)
    if archive_path is None:
        return None
    print(f"Mounting texture pack {os.path.basename(archive_path)}")
    return vfs.add_real_file(model_root.app_id, archive_path)


def _texture_index(display_name):
    """The index LfsFS gave a packed texture, from its "<stem>_NNN.<ext>"
    name - None for anything not named that way."""
    stem = display_name.rsplit(".", 1)[0]
    _, _, index = stem.rpartition("_")
    return int(index) if index.isdigit() else None


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

        # try:
        #     if isinstance(src_value, str):
        #         src_value = int(src_value, 16)
        #     setattr(dst, name, src_value)
        # except TypeError:
        #     setattr(dst, name, hex(src_value))
