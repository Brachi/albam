from collections import Counter, namedtuple
import os
import struct
import zlib

import bpy
from ...exceptions import AlbamCheckFailure
from ...lib.blender import image_to_dds, image_to_tga
from ...registry import blender_registry
from ...vfs import VirtualFileData
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
    absolute_path = model_root.absolute_path if model_root else ""
    content_dir = _pack_content_dir(pack_name, absolute_path)
    return _find_pack_in(content_dir, pack_name) if content_dir else None


def texture_pack_archives(pack_name, model_archive_path):
    """Every copy of texture pack `pack_name` - one per TEXTURE_PACK_FOLDERS
    entry - found the way _texture_pack_archive finds one, as
    [(folder, path)].

    Import reads the best copy only, but writing has to reach all of them:
    which one the game loads is its own setting, and a slot the .tpl gains
    has to exist in whichever pack it loads.
    """
    content_dir = _pack_content_dir(pack_name, model_archive_path)
    if not content_dir:
        return []
    found = []
    for folder in TEXTURE_PACK_FOLDERS:
        path = _find_pack_in(content_dir, pack_name, folders=(folder,))
        if path:
            found.append((folder, path))
    return found


def _pack_content_dir(pack_name, model_archive_path):
    """The content directory holding pack `pack_name`, looked for beside the
    model's archive first (see _texture_pack_archive), or None."""
    candidates = []
    if model_archive_path:
        candidates.append(os.path.dirname(os.path.dirname(model_archive_path)))
    candidates.extend(_PACK_DIRECTORIES)
    candidates.extend(_content_directories_in_vfs())

    seen = set()
    for content_dir in candidates:
        if not content_dir or content_dir in seen:
            continue
        seen.add(content_dir)
        if _find_pack_in(content_dir, pack_name):
            if content_dir in _PACK_DIRECTORIES:
                _PACK_DIRECTORIES.remove(content_dir)
            _PACK_DIRECTORIES.insert(0, content_dir)
            return content_dir
    return None


def _content_directories_in_vfs():
    """Where every other archive the user has added sits, so a model opened
    from outside the install can still reach the install's textures."""
    directories = []
    for vfile in bpy.context.scene.albam.vfs.file_list:
        if vfile.is_root and vfile.absolute_path:
            directories.append(os.path.dirname(os.path.dirname(vfile.absolute_path)))
    return directories


def _find_pack_in(content_dir, pack_name, folders=TEXTURE_PACK_FOLDERS):
    try:
        siblings = {name.lower(): name for name in os.listdir(content_dir)}
    except OSError:
        return None

    for folder in folders:
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
        # A truncated .tpl leaves a partially populated entry list behind
        # (the generated accessor fills it in a `finally`), whose entries
        # point at unread offsets - so reading on is what actually crashes,
        # one line after the code that was meant to handle this.
        print(f"The {tpl_vfile.display_name} is incorrect")
        return None

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

    reread = set()
    for tp in tpl_db:
        textures = packs.get(tp["pack_name"])
        if not textures:
            continue
        tp["pack_name_vfile"] = tp["pack_name"]
        texture = textures.get(tp["texture_id"])
        if texture is None and tp["pack_name"] not in reread:
            # The session's copy of the pack predates one albam rebuilt with
            # textures added (see _PACK_CACHE) - read it again, once.
            reread.add(tp["pack_name"])
            _PACK_CACHE.pop(tp["pack_name"], None)
            textures = packs[tp["pack_name"]] = _load_pack(tp["pack_name"], tp["model_root"])
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
    from .fs import pack_entry_extension
    from .structs.pack import Pack

    with open(pack_path, "rb") as f:
        pack = Pack.from_bytes(f.read())
    pack._read()

    stem = os.path.basename(pack_path).split(".")[0]
    textures = {}
    for index, entry in enumerate(pack.file_entries):
        extension = pack_entry_extension(entry)
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
    custom_properties.pack_entry = texture_name
    custom_properties.source_crc = _crc(data)
    return bl_image


@blender_registry.register_custom_properties_image("tex_cie", ("re4uhd",))
@blender_registry.register_blender_prop
class TexCIECustomProperties(bpy.types.PropertyGroup):
    tpl_id: bpy.props.StringProperty(default="")
    pack_id: bpy.props.StringProperty(default="")
    # Which slot of that .tpl this image came from; -1 for an image albam
    # didn't import (one the user brought in themselves).
    tpl_index: bpy.props.IntProperty(default=-1)
    # The pack entry the image's bytes came from ("44000002_007.dds"), and a
    # CRC-32 of those bytes - what tells an image edited since import from
    # one left alone (see TextureExport). 0 when the scene has neither
    # recorded, and such an image is never written back.
    pack_entry: bpy.props.StringProperty(default="")
    source_crc: bpy.props.IntProperty(default=0)
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
    _NOT_ON_SOURCE = ("tpl_id", "pack_id", "tpl_index", "pack_entry", "source_crc")

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


def _crc(data):
    """A CRC-32 of `data` that fits a Blender IntProperty (signed 32-bit) and
    is never 0, which TexCIECustomProperties.source_crc keeps for unknown."""
    return (zlib.crc32(data) & 0x7FFFFFFF) or 1


# A .tpl, as every character, enemy and room one in the game lays it out: a
# 12-byte header (magic, slot count, offset of the slot table), an 8-byte
# table entry per slot (offset of its info, offset of its palette - always 0
# here), a 36-byte info per slot, the 8-byte (pack id, texture index) each
# info points at, and zero padding to TPL_ALIGNMENT. The handful of system
# .tpl files that carry palettes are not written.
TPL_HEADER_SIZE = 12
TPL_TABLE_ENTRY_SIZE = 8
TPL_INFO_SIZE = 36
TPL_IDS_SIZE = 8
TPL_ALIGNMENT = 32
# Where a tpl_info keeps the offset of its ids (see structs/tpl.ksy).
TPL_INFO_ID_OFFSET = 8
# A material names a slot in one byte, and 0xFF is "no texture".
TPL_MAX_SLOTS = 0xFF

TplSlot = namedtuple("TplSlot", ("info", "pack_id", "texture_id"))


def read_tpl(data):
    """(magic, [TplSlot]) for a .tpl laid out as build_tpl writes one.

    `info` is the slot's 36-byte tpl_info as stored, id offset included;
    build_tpl rewrites that word.
    """
    magic, count, table_offset = struct.unpack_from("<3I", data)
    slots = []
    for i in range(count):
        info_offset, palette_offset = struct.unpack_from(
            "<2I", data, table_offset + i * TPL_TABLE_ENTRY_SIZE)
        if palette_offset:
            raise NotImplementedError(
                "this .tpl carries palettes, which only a few system files do; "
                "albam does not write those")
        info = bytes(data[info_offset:info_offset + TPL_INFO_SIZE])
        ids_offset = struct.unpack_from("<I", info, TPL_INFO_ID_OFFSET)[0]
        pack_id, texture_id = struct.unpack_from("<2I", data, ids_offset)
        slots.append(TplSlot(info, pack_id, texture_id))
    return magic, slots


def build_tpl(magic, slots):
    """A whole .tpl holding `slots`, laid out the way the game's are."""
    count = len(slots)
    infos_start = TPL_HEADER_SIZE + count * TPL_TABLE_ENTRY_SIZE
    ids_start = infos_start + count * TPL_INFO_SIZE

    out = bytearray(struct.pack("<3I", magic, count, TPL_HEADER_SIZE))
    for i in range(count):
        out += struct.pack("<2I", infos_start + i * TPL_INFO_SIZE, 0)
    for i, slot in enumerate(slots):
        info = bytearray(slot.info)
        struct.pack_into("<I", info, TPL_INFO_ID_OFFSET, ids_start + i * TPL_IDS_SIZE)
        out += info
    for slot in slots:
        out += struct.pack("<2I", slot.pack_id, slot.texture_id)
    out += b"\x00" * (-len(out) % TPL_ALIGNMENT)
    return bytes(out)


def _with_size(info, width, height):
    """A tpl_info with its dimensions replaced - stored height first."""
    return struct.pack("<2H", height, width) + info[4:]


def pack_entry_name(pack_id, texture_id, extension):
    """The name a pack entry is exposed under (see fs.pack_entry_extension)."""
    return f"{pack_id:08x}_{texture_id:03d}.{extension}"


def _dds_size(data):
    height, width = struct.unpack_from("<2I", data, 12)
    return width, height


def _tga_size(data):
    return struct.unpack_from("<2H", data, 12)


def _image_current_bytes(bl_image):
    """The bytes the image holds now, or None when only its pixels say -
    painted in Blender, or generated there."""
    if bl_image.is_dirty:
        return None
    if bl_image.packed_file:
        return bytes(bl_image.packed_file.data)
    path = bpy.path.abspath(bl_image.filepath) if bl_image.filepath else ""
    if path and os.path.isfile(path):
        with open(path, "rb") as f:
            return f.read()
    return None


def _image_was_edited(bl_image, custom_properties):
    """Whether an imported image no longer holds the bytes it came with.

    Blender keeps a packed image's bytes when its file path changes, so this
    is what an edit looks like: pixels painted over, or the image unpacked
    and its file replaced. An image with no CRC recorded never reads as
    edited.
    """
    if not custom_properties.source_crc:
        return False
    current = _image_current_bytes(bl_image)
    if not current and not any(bl_image.size):
        # Neither bytes nor pixels: its file went missing (unpacked, then
        # moved or deleted). That is not an edit, and treating it as one
        # would overwrite the shipped texture with an empty one.
        raise AlbamCheckFailure(
            f"Image {bl_image.name} has no data",
            details=f"It was imported from {custom_properties.pack_entry}, but "
                    f"Blender can't load it any more, so there is nothing to export",
            solution="Check the image's file path, or pack it back into the .blend",
        )
    return current is None or _crc(current) != custom_properties.source_crc


def _encode_like(bl_image, original):
    """(bytes, extension) for `bl_image`, in the format of `original` - the
    texture it stands in for - unless it already is a DDS.

    A DDS the user supplies goes in as it is: it was made for the game on
    purpose. Anything else is encoded from its pixels the way the texture it
    replaces was - across the packs of an install that is DXT1, DXT3, DXT5,
    uncompressed A8R8G8B8, or a TGA, about half of all entries being TGA.
    DXT1 and DXT5 stay what they were, DXT3 becomes DXT5 (alpha kept, and
    nothing here encodes DXT3), uncompressed stays uncompressed, and a mip
    chain is written only if the original had one.
    """
    current = _image_current_bytes(bl_image)
    if current and current[:4] == b"DDS ":
        return current, "dds"
    if original[:4] != b"DDS ":
        return image_to_tga(bl_image), "tga"
    fourcc = original[84:88]
    has_mipmaps = struct.unpack_from("<I", original, 28)[0] > 1
    if not fourcc.strip(b"\x00"):
        return image_to_dds(bl_image, None), "dds"
    fourcc = "DXT1" if fourcc == b"DXT1" else "DXT5"
    return image_to_dds(bl_image, fourcc, mipmaps=has_mipmaps), "dds"


def _find_vfile(display_name):
    for vfile in bpy.context.scene.albam.vfs.file_list:
        if vfile.display_name == display_name and not vfile.is_root:
            return vfile
    return None


class TextureExport:
    """What a model's textures add to its export.

    Three kinds of image can be bound to a material:

    - one imported from this model's own .tpl: written as the slot it came
      from. If it was edited since (see _image_was_edited), its pack entry is
      rewritten too - which every model sharing that pack sees, but the edit
      was to that very texture.
    - one imported from somewhere else: its pack entry stays as it is, and
      the .tpl gains a slot pointing at it.
    - one albam did not import: it is appended to the pack this .tpl draws
      from, and the .tpl gains a slot for it. Nothing that already exists
      changes, so no other model sharing the pack or the .tpl is affected.

    `bindings` is [(bl_material, field, bl_image)], `field` being the
    material's slot field the image is bound to; `carried` is
    {(bl_material name, field): slot} as the material held it on import.

    After construction, `slots` maps an image name to the slot to write,
    `vfiles` holds the .tpl and pack entries to export beside the model, and
    `num_slots` is the .tpl's new slot count, or None if it did not grow.
    """

    def __init__(self, app_id, model_name, tpl_id, bindings, carried):
        self.app_id = app_id
        self.model_name = model_name
        self.slots = {}
        self.vfiles = []
        self.num_slots = None

        self._tpl_id = tpl_id or self._tpl_id_from_images(bindings)
        # Found up front when it can be: its archive is where packs are
        # looked for, which an edited texture needs whether or not the .tpl
        # itself changes.
        self._tpl_vfile = _find_vfile(self._tpl_id) if self._tpl_id else None
        self._packs = {}
        # Pack entry name -> the bytes it is being rewritten with.
        self._replaced = {}

        pending = []
        seen = set()
        for bl_material, field, bl_image in bindings:
            if bl_image.name in seen:
                continue
            seen.add(bl_image.name)
            custom_properties = bl_image.albam_custom_properties.get_custom_properties_for_appid(
                app_id)
            imported = custom_properties.tpl_index >= 0 and custom_properties.pack_entry
            if imported and _image_was_edited(bl_image, custom_properties):
                self._replace_pack_entry(bl_image, custom_properties)
            # A slot with no .tpl recorded beside it is taken to be one of
            # this model's: nothing says otherwise.
            own = custom_properties.tpl_id in ("", self._tpl_id)
            if custom_properties.tpl_index >= 0 and own:
                self.slots[bl_image.name] = custom_properties.tpl_index
            else:
                pending.append((bl_material, field, bl_image, custom_properties))

        if pending:
            self._add_slots(pending, carried)

    def _tpl_id_from_images(self, bindings):
        """The .tpl most of the model's imported images came from - for a
        model whose mesh has no .tpl recorded."""
        counts = Counter()
        for _, _, bl_image in bindings:
            custom_properties = bl_image.albam_custom_properties.get_custom_properties_for_appid(
                self.app_id)
            if custom_properties.tpl_index >= 0 and custom_properties.tpl_id:
                counts[custom_properties.tpl_id] += 1
        return counts.most_common(1)[0][0] if counts else ""

    def _pack(self, pack_id):
        """{texture index: (name, bytes)} of one pack."""
        if pack_id not in self._packs:
            root = self._tpl_vfile.root_vfile if self._tpl_vfile else None
            self._packs[pack_id] = _load_pack(f"{pack_id:08x}", root)
        textures = self._packs[pack_id]
        if not textures:
            raise AlbamCheckFailure(
                f"Texture pack {pack_id:08x} of {self.model_name} wasn't found",
                details="Exporting a changed or added texture means reading the pack "
                        "it goes into, and albam looks for it beside the model's "
                        "archive and beside every archive added to the VFS",
                solution="Add the model's archive from the game folder to the VFS, "
                         "or any archive that sits beside the ImagePack folders",
            )
        return textures

    def _entry_count_on_disk(self, pack_id):
        """How many entries pack `pack_id` holds on disk now, which is what a
        texture added to it is numbered from.

        Not the session's cached copy (see _PACK_CACHE): once a pack albam
        rebuilt has been installed, the cache still holds the pack as first
        read, and numbering from it would give new textures the numbers the
        installed pack already uses - which Pack item then reads as
        replacements, silently overwriting the textures added before. The
        copies counted are the ones Pack item rewrites
        (archive.texture_pack_companions), so they have to agree: a pack
        whose SD and HD copies hold different counts has no number a new
        texture could take in both.
        """
        from .archive import pack_entry_count

        pack_name = f"{pack_id:08x}"
        root = self._tpl_vfile.root_vfile if self._tpl_vfile else None
        copies = texture_pack_archives(pack_name, root.absolute_path if root else "")
        if not copies:
            raise AlbamCheckFailure(
                f"Texture pack {pack_name} of {self.model_name} wasn't found on disk",
                details="A new texture is appended to the pack the model draws from, "
                        "and Pack item rewrites that pack's copies on disk",
                solution="Add the model's archive from the game folder to the VFS, "
                         "or any archive that sits beside the ImagePack folders",
            )
        counts = {path: pack_entry_count(path) for _, path in copies}
        if len(set(counts.values())) > 1:
            listed = ", ".join(f"{path}: {count}" for path, count in counts.items())
            raise AlbamCheckFailure(
                f"The copies of texture pack {pack_name} hold different numbers of "
                f"textures",
                details=f"{listed}. A texture added to the pack has to get the same "
                        f"number in every copy, since the game loads whichever its "
                        f"texture setting picks",
                solution="Install every copy Pack item wrote for this pack, or restore "
                         "the originals",
            )
        count = next(iter(counts.values()))
        cached = _PACK_CACHE.get(pack_name)
        if cached is not None and len(cached) != count:
            # Read again on next use, so re-importing sees what is installed.
            _PACK_CACHE.pop(pack_name)
            self._packs.pop(pack_id, None)
        return count

    def _replace_pack_entry(self, bl_image, custom_properties):
        name = custom_properties.pack_entry
        pack_id = int(custom_properties.pack_id, 16)
        texture_id = _texture_index(name)
        _, original = self._pack(pack_id)[texture_id]
        data, _ = _encode_like(bl_image, original)
        self._replaced[name] = data
        self.vfiles.append(VirtualFileData(self.app_id, name, data_bytes=data))

    def _load_tpl(self):
        if self._tpl_vfile is None:
            raise AlbamCheckFailure(
                f"{self.model_name} has a texture its .tpl doesn't, and the .tpl "
                f"isn't in the VFS to add it to",
                details=f"A new texture is added as a slot of the model's .tpl "
                        f"({self._tpl_id or 'unknown'}), which is read from the "
                        f"archive the model came from",
                solution="Add the model's archive back to the VFS and export again",
            )
        return read_tpl(self._tpl_vfile.get_bytes())

    def _add_slots(self, pending, carried):
        magic, slots = self._load_tpl()
        original_count = len(slots)
        if not slots:
            raise AlbamCheckFailure(
                f"{self._tpl_id} has no slots, so there is no pack to add a texture to",
                solution="Re-point the material at a texture the model already has",
            )
        # A .tpl draws from one pack in practice; a new texture goes into the
        # one it draws from most.
        target_pack = Counter(slot.pack_id for slot in slots).most_common(1)[0][0]
        next_texture_id = self._entry_count_on_disk(target_pack)

        for bl_material, field, bl_image, custom_properties in pending:
            template = slots[0]
            carried_slot = carried.get((bl_material.name, field))
            if carried_slot is not None and carried_slot < original_count:
                # The texture this image took the place of, which says what
                # kind of texture the slot holds (format, filtering, wrap).
                template = slots[carried_slot]
            _, template_bytes = self._pack(template.pack_id)[template.texture_id]

            if custom_properties.pack_entry:
                # Imported from another .tpl: the texture is already in a
                # pack - rewritten there above if it was edited - and only
                # needs a slot here.
                name = custom_properties.pack_entry
                pack_id = int(custom_properties.pack_id, 16)
                texture_id = _texture_index(name)
                data = self._replaced.get(name) or self._pack(pack_id)[texture_id][1]
            else:
                data, extension = _encode_like(bl_image, template_bytes)
                pack_id, texture_id = target_pack, next_texture_id
                next_texture_id += 1
                self.vfiles.append(VirtualFileData(
                    self.app_id, pack_entry_name(pack_id, texture_id, extension),
                    data_bytes=data))

            width, height = _dds_size(data) if data[:4] == b"DDS " else _tga_size(data)
            slots.append(TplSlot(_with_size(template.info, width, height), pack_id, texture_id))
            self.slots[bl_image.name] = len(slots) - 1

        if len(slots) > TPL_MAX_SLOTS:
            raise AlbamCheckFailure(
                f"{self._tpl_id} would need {len(slots)} texture slots",
                details=f"A material names its texture by a one-byte slot, and "
                        f"0xFF means none, so a .tpl holds at most {TPL_MAX_SLOTS}",
                solution="Use fewer distinct new images",
            )
        self.num_slots = len(slots)
        self.vfiles.append(VirtualFileData(
            self.app_id, self._tpl_id, data_bytes=build_tpl(magic, slots)))
