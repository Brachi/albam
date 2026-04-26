"""
RE4 UHD texture loading: TPL metadata + PACK pixel data -> Blender images.

Flow:
  1. The UDAS contains .TPL file entries alongside the mesh .BINs.
     Each TPL holds metadata: PackID, TextureID, width, height.
  2. A .pack.lfs file (same directory as the .lfs) contains the actual image data.
     Its first u32 = PackID, matching the TPL entry.
  3. TextureID indexes into the pack's offset table -> raw image bytes.
  4. Image bytes start with a magic: 0x20534444 = DDS, 0x00020000 = TGA.
  5. Written to a temp file and loaded via bpy.data.images.load().

Limitations:
  - TPL slot indices in each BIN's materials are relative to the set of TPL entries
    that belong to that BIN. Currently all TPL entries in the UDAS are read together
    and treated as a global list, which works correctly for the main body BIN (_000)
    but may assign incorrect textures to secondary BINs (head, hands, etc.) if their
    TPL entries are not at the start of the global list.
  - Mods such as the HD Project route certain textures (e.g. Leon's head) through a
    separate .pack.lfs file (e.g. 07000000.pack.lfs). The code will find this file if
    it is placed in the same directory, but only if the TPL entry for that BIN is
    correctly identified in the UDAS — which is not guaranteed with the current
    global-list approach. See README for details.
"""

import os
import struct
import tempfile
import bpy
from ...albam_vendor import xcompress
from .material import _create_cie_shader
from .structs.lfs import Lfs
from .structs.tpl import Tpl


def new_load_textures_for_model(mesh_ob, bin, vfile):
    image_cache = {}
    me = mesh_ob.data
    textures_db = _process_tpls(vfile)
    for mat in bin.materials:
        mat.diffuse_map
        mat.bump_map
        mat.opacity_map
        mat.special_special_map
    # for tex in textures_db:
    #    if tex["vfile"] is not None:
    #        _create_blender_image_from_tex(tex)
    #    else:
    #        print(f"{tex['tpl_name']} has no associated texture file in the archive")
    for bl_mat in me.materials:
        if bl_mat is None:
            continue
        diffuse_slot = bl_mat.get("re4uhd_diffuse_tpl_slot", -1)
        bump_slot = bl_mat.get("re4uhd_bump_tpl_slot",    -1)
        opacity_slot = bl_mat.get("re4uhd_opacity_tpl_slot", -1)
        _create_cie_shader(bl_mat, image_cache, diffuse_slot, bump_slot, opacity_slot)


def load_textures_for_model(mesh_ob, bin, vfile, context):
    """
    Entry point: find pack files, parse TPLs from UDAS, assign to materials.
    """
    lfs_path = vfile.root_vfile.absolute_path
    lfs_dir = os.path.dirname(lfs_path)

    pack_db = _build_pack_db(lfs_dir)
    if not pack_db:
        print("[re4uhd] textures: no .pack.lfs files found — skipping texture load")
        return

    print(f"[re4uhd] textures: found {len(pack_db)} pack file(s): "
          f"{[hex(k) for k in pack_db]}")

    tpl_list = _read_tpl_entries(lfs_path)
    if not tpl_list:
        print("[re4uhd] textures: no TPL entries found in UDAS")
        return

    print(f"[re4uhd] textures: {len(tpl_list)} TPL entries parsed")

    image_cache = {}
    for slot_i, tpl in enumerate(tpl_list):
        pack_id = tpl["pack_id"]
        tex_id = tpl["texture_id"]
        if pack_id not in pack_db:
            print(
                f"[re4uhd]   slot {slot_i}: pack_id=0x{pack_id:08X} not found "
                f"(available: {[hex(k) for k in pack_db]}). "
                f"Place the matching .pack.lfs in the same directory."
            )
            continue
        img = _load_image_from_pack(pack_db[pack_id], tex_id, slot_i, pack_id)
        if img:
            image_cache[slot_i] = img
            print(f"[re4uhd]   slot {slot_i}: loaded '{img.name}' "
                  f"({tpl['width']}x{tpl['height']})")

    if not image_cache:
        print("[re4uhd] textures: no images loaded")
        return

    me = mesh_ob.data
    for bl_mat in me.materials:
        if bl_mat is None:
            continue
        diffuse_slot = bl_mat.get("re4uhd_diffuse_tpl_slot", -1)
        bump_slot = bl_mat.get("re4uhd_bump_tpl_slot",    -1)
        opacity_slot = bl_mat.get("re4uhd_opacity_tpl_slot", -1)
        _create_cie_shader(bl_mat, image_cache, diffuse_slot, bump_slot, opacity_slot)

    print("[re4uhd] textures: materials set up")


# -- Pack database -------------------------------------------------------------

def _build_pack_db(directory):
    """
    Scan directory for *.pack.lfs files, decompress each, read PackID.
    Returns dict: {pack_id (int) -> raw_pack_bytes}
    """
    pack_db = {}
    for fname in os.listdir(directory):
        if not fname.lower().endswith(".pack.lfs"):
            continue
        fpath = os.path.join(directory, fname)
        try:
            raw = _decompress_lfs(fpath)
            if len(raw) < 8:
                continue
            pack_id = struct.unpack_from("<I", raw, 0)[0]
            pack_db[pack_id] = raw
            print(f"[re4uhd]   pack: {fname} -> PackID=0x{pack_id:08X}")
        except Exception as e:
            print(f"[re4uhd]   pack: failed to read {fname}: {e}")
    return pack_db


def _decompress_lfs(file_path):
    lfs = Lfs.from_file(file_path)
    lfs._read()
    return xcompress.xcompress_decompress_re4hd(lfs.file_entries)


# -- TPL parsing ---------------------------------------------------------------

def _read_tpl_entries(lfs_path):
    """
    Read all TPL entries from the UDAS, in order of appearance.

    The returned list is used as a global texture slot table: material fields
    diffuse_slot, bump_slot and opacity_slot are indices into this list.
    """
    from .structs.udas import Udas
    raw_lfs = _decompress_lfs(lfs_path)
    udas = Udas.from_bytes(raw_lfs)
    udas._read()

    tpl_entries = []
    entries = udas.header.data_blocks.file_entries
    exts = udas.header.data_blocks.file_extension

    for fe, ext_obj in zip(entries, exts):
        if ext_obj.ext.upper() != "TPL":
            continue
        raw = bytes(fe.raw_data)
        if len(raw) < 12:
            continue
        tpl = _parse_tpl(raw)
        if tpl:
            tpl_entries.extend(tpl)

    return tpl_entries


def _parse_tpl(raw):
    """
    Parse a single TPL blob. Returns list of {pack_id, texture_id, width, height}.

    TPL layout:
      u4 magic  (0x78563412 or 0x12345678)
      u4 TplAmount
      u4 offsetToOffsetArea
      -- at offsetToOffsetArea --
      TplAmount * (u4 image_data_offset, u4 palette_offset)
      -- at each image_data_offset --
      u2 height, u2 width, u4 PixelFormatType, u4 secondaryOffset
      u4 Wrap_S, u4 Wrap_T, u4 Min_Filter, u4 Mag_Filter
      f4 Lod_Bias, u1 Enable_Lod, u1 Min_Lod, u1 Max_Lod, u1 Is_Compressed
      -- at secondaryOffset --
      u4 PackID, u4 TextureID
    """
    if len(raw) < 12:
        return []
    magic = struct.unpack_from("<I", raw, 0)[0]
    if magic not in (0x78563412, 0x12345678):
        return []
    tpl_amount, offset_area = struct.unpack_from("<II", raw, 4)
    if tpl_amount == 0 or tpl_amount > 0x10000:
        return []

    results = []
    pos = offset_area
    for _ in range(tpl_amount):
        if pos + 8 > len(raw):
            break
        img_offset, _ = struct.unpack_from("<II", raw, pos)
        pos += 8
        if img_offset == 0 or img_offset + 20 > len(raw):
            results.append(None)
            continue
        height, width, _, sec_offset = struct.unpack_from("<HHII", raw, img_offset)
        if sec_offset == 0 or sec_offset + 8 > len(raw):
            results.append(None)
            continue
        pack_id, texture_id = struct.unpack_from("<II", raw, sec_offset)
        results.append({"pack_id": pack_id, "texture_id": texture_id,
                        "width": width, "height": height})

    return [r for r in results if r is not None]


# -- Image extraction ----------------------------------------------------------

def _load_image_from_pack(pack_raw, texture_id, slot_i, pack_id):
    if len(pack_raw) < 8:
        return None
    amount = struct.unpack_from("<I", pack_raw, 4)[0]
    if texture_id >= amount:
        return None
    offset_pos = 8 + texture_id * 4
    if offset_pos + 4 > len(pack_raw):
        return None
    data_offset = struct.unpack_from("<I", pack_raw, offset_pos)[0]
    if data_offset == 0 or data_offset + 16 >= len(pack_raw):
        return None
    file_length = struct.unpack_from("<I", pack_raw, data_offset)[0]
    image_start = data_offset + 16
    image_end = min(image_start + file_length, len(pack_raw))
    image_bytes = pack_raw[image_start:image_end]
    if len(image_bytes) < 4:
        return None
    magic = struct.unpack_from("<I", image_bytes, 0)[0]
    if magic == 0x20534444:
        ext = ".dds"
    elif magic in (0x00020000, 0x000A0000):
        ext = ".tga"
    else:
        print(f"[re4uhd]   slot {slot_i}: unknown image magic 0x{magic:08X}")
        return None
    tmp_path = os.path.join(
        tempfile.gettempdir(),
        f"re4uhd_p{pack_id:08x}_t{texture_id:04d}{ext}"
    )
    with open(tmp_path, "wb") as f:
        f.write(image_bytes)
    try:
        img = bpy.data.images.load(tmp_path, check_existing=True)
        img.name = f"re4uhd_p{pack_id:08x}_t{texture_id:04d}"
        img.pack()
        os.remove(tmp_path)
        return img
    except Exception as e:
        print(f"[re4uhd]   slot {slot_i}: failed to load image: {e}")
        return None


def _process_tpls(vfile_bin, root_id):
    # Process TPLs in a scope of the container with BIN file
    # root_id = vfile_bin.tree_node.root_id
    print(f"Processing TPLs for root_id: {root_id}")
    vf_list = bpy.context.scene.albam.vfs.file_list
    tpl_vfiles = [vf for vf in vf_list if vf.tree_node.root_id ==
                  root_id and vf.display_name.endswith(".TPL")]
    tpl_db = []
    for vfile in tpl_vfiles:
        print(f"TPL is: {vfile.display_name}")
        tpl_bytes = vfile.get_bytes()
        tpl = Tpl.from_bytes(tpl_bytes)
        tpl._read()
        try:
            tpl.tpl_entries
        except EOFError:
            print(f"The {vfile.display_name} is incorrect")
            continue
        for i, te in enumerate(tpl.tpl_entries):
            tpl_entry = {
                "tpl_name": vfile.display_name,
                "pack_name": str(hex(te.image_data.ids.pack_id))[2:],
                "pack_name_vfile": "",
                "texture_id": te.image_data.ids.texture_id,
                "width": te.image_data.width,
                "height": te.image_data.height,
                "vfile": None
            }

            tpl_db.append(tpl_entry)
            print(f"Texture size: {te.image_data.width}x{te.image_data.height}")
            print("Pack: {}, Texture ID: {} ".format(tpl_entry["pack_name"], tpl_entry["texture_id"]))
    return _process_tex_indices(tpl_db)


def _process_tex_indices(tpl_db):
    vfile_list = bpy.context.scene.albam.vfs.file_list
    cached_packs = {}
    for tp in tpl_db:
        pack_found = False
        pack_name = tp["pack_name"]
        if pack_name not in cached_packs.keys():
            for vfile in vfile_list:
                if vfile.display_name.startswith(pack_name) and vfile.is_root:
                    print(f"found {vfile.display_name}!")
                    tp["pack_name_vfile"] = vfile.display_name
                    pack_found = True
                    cached_packs[vfile.display_name] = vfile.name
        if not pack_found:
            print(f"{pack_name} wasn't found")

    tex_db = {}
    for pack_name, root_id in cached_packs.items():
        tex_list = []
        for vfile in vfile_list:
            if vfile.tree_node.root_id == root_id:
                print(f"loading textures from {vfile.display_name}")
                # tex_list.append(vfile.display_name)
                tex_list.append(vfile)
        tex_db[pack_name] = tex_list

    for tp in tpl_db:
        tex_pack = tex_db.get(tp["pack_name_vfile"], [None])
        tp["vfile"] = tex_pack[tp["texture_id"]]

    return tpl_db


def _create_textures(tpl_db, tex_db,):
    # tex_db = {"id.pack.lfs"[id_000.dds, id_001.dds, ...], ...}
    vfile_list = bpy.context.scene.albam.vfs.file_list
    for tpl in tpl_db:
        for pack_name, pack_textures in tex_db.items():
            if tpl["pack_name"] in pack_name:
                try:
                    tex = pack_textures[tpl["texture_id"]]
                except IndexError:
                    print(f"Texture with id {tpl['texture_id']} wasn't found in {pack_name}")
                    continue
                for vfile in vfile_list:
                    if vfile.display_name == tex:
                        print(f"Loading {tex} from {vfile.display_name}")
                        _create_blender_image_from_tex(tpl, vfile)
                        print(f"Texture size: {tpl['width']}x{tpl['height']}")


def _create_blender_image_from_tex(tpl):
    vfile = tpl["vfile"]
    tex = vfile.get_bytes()

    bl_image = bpy.data.images.new(f"{vfile.display_name}", tpl["width"], tpl["height"])
    bl_image.source = "FILE"
    bl_image.pack(data=tex, data_len=len(tex))
    return bl_image
