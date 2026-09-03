import os

import bpy
from ...registry import blender_registry
from .structs.tpl import Tpl

# The content sub-folders holding texture packs, best first: this release
# ships both the original packs and higher-resolution replacements under the
# same pack id, and a .tpl entry names only the id.
TEXTURE_PACK_FOLDERS = ("ImagePackHD", "ImagePack")

# Content directories a texture pack has been found in this session, most
# recent first. A model archive being modded is often somewhere else
# entirely - a working folder, not the install - and its textures still have
# to come from somewhere, so a directory that worked once is remembered and
# tried for later archives that have no pack folders of their own.
_PACK_DIRECTORIES = []

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
    candidates = []
    absolute_path = model_root.absolute_path if model_root else ""
    if absolute_path:
        candidates.append(os.path.dirname(os.path.dirname(absolute_path)))
    candidates.extend(_PACK_DIRECTORIES)
    candidates.extend(_content_directories_in_vfs())

    seen = set()
    for content_dir in candidates:
        if not content_dir or content_dir in seen:
            continue
        seen.add(content_dir)
        found = _find_pack_in(content_dir, pack_name)
        if found:
            if content_dir in _PACK_DIRECTORIES:
                _PACK_DIRECTORIES.remove(content_dir)
            _PACK_DIRECTORIES.insert(0, content_dir)
            return found
    return None


def _content_directories_in_vfs():
    """Where every other archive the user has added sits, so a model opened
    from outside the install can still reach the install's textures."""
    directories = []
    for vfile in bpy.context.scene.albam.vfs.file_list:
        if vfile.is_root and vfile.absolute_path:
            directories.append(os.path.dirname(os.path.dirname(vfile.absolute_path)))
    return directories


def _find_pack_in(content_dir, pack_name):
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
        # A pack ships either compressed, as a ".lfs", or as a plain file
        # sitting on its own - a tenth of the packs a sampled set of models
        # referenced are the plain kind, and skipping those cost those models
        # their textures. The compressed one is preferred where both exist.
        found = [name for name in names if name.lower().startswith(pack_name)]
        for name in sorted(found, key=lambda n: not n.lower().endswith(".lfs")):
            return os.path.join(pack_dir, name)
    return None


def _process_tpls(tpl_vfile):
    """Every texture entry of one .tpl, resolved to the bytes behind it."""
    tpl_db = []
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
                print(f"{pack_name} texture pack wasn't found - looked beside "
                      f"this archive and beside every other one added")

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
    if archive_path.lower().endswith(".lfs"):
        pack_fs = LfsFS(archive_path)
        try:
            textures = {}
            for path in pack_fs.walk.files():
                name = path.lstrip("/")
                index = _texture_index(name)
                if index is not None:
                    textures[index] = (name, pack_fs.readbytes(path))
        finally:
            pack_fs.close()
    else:
        textures = _read_plain_pack(archive_path)

    _PACK_CACHE[pack_name] = textures
    return textures


def _read_plain_pack(pack_path):
    """A pack stored uncompressed, with no .lfs around it.

    Named the same way its entries are numbered elsewhere (see
    albam/engines/cie/fs.py), so a texture resolves by index either way.
    """
    from .structs.pack import Pack

    with open(pack_path, "rb") as f:
        pack = Pack.from_bytes(f.read())
    pack._read()

    stem = os.path.basename(pack_path).split(".")[0]
    textures = {}
    for index, entry in enumerate(pack.file_entries):
        extension = "dds" if entry.data.is_dds else "tga"
        textures[index] = (f"{stem}_{index:03d}.{extension}", entry.data.raw_data)
    return textures


def _texture_index(display_name):
    """The index a packed texture was numbered with, from its
    "<stem>_NNN.<ext>" name - None for anything not named that way."""
    stem = display_name.rsplit(".", 1)[0]
    _, _, index = stem.rpartition("_")
    return int(index) if index.isdigit() else None


def _image_name(app_id, texture_name, tpl_index):
    """The datablock name to import this texture under.

    Images are shared between the models of an archive - one pack serves all
    of them, and a character archive holds dozens of models. But the .tpl
    slot recorded on an image is only true for models whose .tpl puts that
    texture at that slot, and an archive holds many .tpl files that need not
    agree. Export reads the slot back off the image (see mesh._texture_slot),
    so a shared image carrying another .tpl's slot writes a material pointing
    at the wrong texture - correct-looking in Blender and wrong in the game.

    So the texture's own name is used while the slot agrees, and a texture
    that lands on a different slot gets a datablock of its own. Sharing is
    what happens in the common case; duplicating only where it has to.

    No shipped archive is known to need this: every .tpl of a sampled
    archive agrees on where a given packed texture sits. It is a guard on an
    invariant the format does not state, not a fix for an observed failure.
    """
    bl_image = bpy.data.images.get(texture_name)
    if bl_image is None:
        return texture_name
    custom_properties = bl_image.albam_custom_properties.get_custom_properties_for_appid(app_id)
    if custom_properties.tpl_index == tpl_index:
        return texture_name
    return f"{texture_name}@{tpl_index}"


def _create_blender_image_from_tex(tpl):
    app_id = "re4uhd"
    texture_name = tpl.get("texture_name")
    data = tpl.get("texture_bytes")
    if not texture_name or not data:
        return None

    name = _image_name(app_id, texture_name, tpl["tpl_index"])
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
