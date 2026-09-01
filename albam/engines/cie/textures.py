import os

import bpy
from ...registry import blender_registry
from .structs.tpl import Tpl

# The content sub-folders holding texture packs, best first: this release
# ships both the original packs and higher-resolution replacements under the
# same pack id, and a .tpl entry names only the id.
TEXTURE_PACK_FOLDERS = ("ImagePackHD", "ImagePack")

# pack id -> {texture index: (name, bytes)}, for this Blender session.
# Reading a pack means decompressing a whole archive, and one is shared by
# every model in a character archive, so it is read once. It also keeps
# textures resolvable for a model re-imported from an export root, which has
# no path on disk to find the pack from.
_PACK_CACHE = {}


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
            # The slot a material addresses this texture by. Export reads it
            # back off the image to rebuild the material's texture indices.
            "tpl_index": i,
            "tpl_name": tpl_vfile.display_name,
            "tpl_entry": te,
            "pack_name": f"{te.image_data.ids.pack_id:08x}",
            "pack_name_vfile": "",
            "model_root": tpl_vfile.root_vfile,
            "texture_name": None,
            "texture_bytes": None,
            "texture_id": te.image_data.ids.texture_id,
            "width": te.image_data.width,
            "height": te.image_data.height,
        }

        tpl_db.append(tpl_entry)
        # print(f"Texture size: {te.image_data.width}x{te.image_data.height}")
        # print("Pack: {}, Texture ID: {} ".format(tpl_entry["pack_name"], tpl_entry["texture_id"]))
    return _process_tex_indices(tpl_db)


def _process_tex_indices(tpl_db):
    """Resolve every TPL entry to the bytes of the texture it names.

    A .tpl doesn't name its textures: an entry carries a pack id and an index
    into that pack (see structs/tpl.ksy), and the pack is a separate archive.
    It is used if the user has already added it, and otherwise opened straight
    off disk - see _load_pack, which explains why it isn't mounted.
    """
    packs = {}  # pack_name : {texture index : (name, bytes)}
    for tp in tpl_db:
        pack_name = tp["pack_name"]
        if pack_name not in packs:
            packs[pack_name] = _load_pack(pack_name, tp["model_root"])
            if not packs[pack_name]:
                print(f"{pack_name} texture pack wasn't found")

    if not any(packs.values()):
        return None

    for tp in tpl_db:
        textures = packs.get(tp["pack_name"])
        if not textures:
            continue
        tp["pack_name_vfile"] = tp["pack_name"]
        texture = textures.get(tp["texture_id"])
        if texture is None:
            raise RuntimeError(
                "Texture {} not found in pack {}".format(tp["texture_id"], tp["pack_name"])
            )
        tp["texture_name"], tp["texture_bytes"] = texture
    return tpl_db


def _load_pack(pack_name, model_root):
    """{texture index: (name, bytes)} for one texture pack.

    Reads the pack rather than adding it to the VFS. Adding a root mid-import
    would reallocate the file list, and Blender invalidates every reference
    into a CollectionProperty when it grows - including the one the import
    operator is holding to write back onto the imported object once the
    import function returns.

    A pack the user added themselves is read through the VFS; otherwise it is
    opened directly from the archive next to the model (see
    _texture_pack_archive).
    """
    from .fs import LfsFS

    cached = _PACK_CACHE.get(pack_name)
    if cached:
        return cached

    for vfile in bpy.context.scene.albam.vfs.file_list:
        if vfile.is_root and pack_name in vfile.display_name:
            root_id = vfile.name
            textures = {}
            for entry in bpy.context.scene.albam.vfs.file_list:
                if entry.tree_node.root_id != root_id or entry.is_root:
                    continue
                index = _texture_index(entry.display_name)
                if index is not None:
                    textures[index] = (entry.display_name, entry.get_bytes())
            _PACK_CACHE[pack_name] = textures
            return textures

    archive_path = _texture_pack_archive(pack_name, model_root)
    if archive_path is None:
        return {}

    print(f"Reading texture pack {os.path.basename(archive_path)}")
    pack_fs = LfsFS(archive_path)
    try:
        textures = {}
        for path in pack_fs.walk.files():
            name = path.lstrip("/")
            index = _texture_index(name)
            if index is not None:
                textures[index] = (name, pack_fs.readbytes(path))
        _PACK_CACHE[pack_name] = textures
        return textures
    finally:
        pack_fs.close()


def _texture_index(display_name):
    """The index a packed texture was numbered with, from its
    "<stem>_NNN.<ext>" name - None for anything not named that way."""
    stem = display_name.rsplit(".", 1)[0]
    _, _, index = stem.rpartition("_")
    return int(index) if index.isdigit() else None


def _create_blender_image_from_tex(tpl):
    app_id = "re4uhd"
    name = tpl.get("texture_name")
    data = tpl.get("texture_bytes")
    if not name or not data:
        return None

    bl_image = bpy.data.images.get(name)
    if bl_image:
        return bl_image

    # Dimensions come from the packed file's own header once Blender reads it;
    # the .tpl's are the original pack's, which the higher-resolution packs
    # don't match.
    bl_image = bpy.data.images.new(name, tpl["width"], tpl["height"])
    bl_image.source = "FILE"
    bl_image.pack(data=data, data_len=len(data))

    bl_image.albam_asset.app_id = app_id
    custom_properties = bl_image.albam_custom_properties.get_custom_properties_for_appid(app_id)
    custom_properties.set_from_source(tpl["tpl_entry"].image_data)
    custom_properties.tpl_id = tpl["tpl_name"]
    custom_properties.pack_id = tpl["pack_name"]
    custom_properties.tpl_index = tpl["tpl_index"]
    return bl_image


@blender_registry.register_custom_properties_image("tex_cie", ("re4uhd",))
@blender_registry.register_blender_prop
class TexCIECustomProperties(bpy.types.PropertyGroup):
    tpl_id: bpy.props.StringProperty(default="")
    pack_id: bpy.props.StringProperty(default="")
    # Which slot of that .tpl this image came from; -1 for an image albam
    # didn't import (one the user brought in themselves).
    tpl_index: bpy.props.IntProperty(default=-1)
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
    # Set by the importer from the .tpl entry, not present on it.
    _NOT_ON_SOURCE = ("tpl_id", "pack_id", "tpl_index")

    def set_from_source(self, mesh):
        # XXX assume only properties are part of annotations
        for attr_name in self.__annotations__:
            if attr_name in self._NOT_ON_SOURCE:
                continue
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
