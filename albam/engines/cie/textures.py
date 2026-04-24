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
from .structs.lfs import Lfs

RE4UHD_NORMAL_GROUP_NAME = "RE4 UHD Normal Map"


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
        _setup_material_nodes(bl_mat, image_cache, diffuse_slot, bump_slot, opacity_slot)

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


# -- Material node setup -------------------------------------------------------

def _get_or_create_normal_group():
    """
    Create (once) a node group for RE4 UHD's swizzled normal map format.

    RE4 UHD stores normals with X in the R channel (G and B are identical to R)
    and Y in the Alpha channel. Z is not stored and must be approximated.
    Using B=1.0 as the Z approximation is accurate for typical surface normals
    and avoids unnecessary math node complexity.

    Compatible with Blender 4.x and 5.x (no deprecated RGB nodes).
    """
    existing = bpy.data.node_groups.get(RE4UHD_NORMAL_GROUP_NAME)
    if existing:
        return existing

    g = bpy.data.node_groups.new(RE4UHD_NORMAL_GROUP_NAME, "ShaderNodeTree")

    def new_socket(name, in_out, stype):
        if hasattr(g, "interface"):
            return g.interface.new_socket(name=name, in_out=in_out, socket_type=stype)
        col = g.inputs if in_out == "INPUT" else g.outputs
        return col.new(stype, name)

    new_socket("Color",  "INPUT",  "NodeSocketColor")
    new_socket("Alpha",  "INPUT",  "NodeSocketFloat")
    new_socket("Normal", "OUTPUT", "NodeSocketVector")

    def n(node_type, loc):
        nd = g.nodes.new(node_type)
        nd.location = loc
        return nd

    lk = g.links.new

    group_in = n("NodeGroupInput",  (-600, 0))
    group_out = n("NodeGroupOutput", (600, 0))

    # X from Red channel, Y from Alpha, Z approximated as 1.0 (neutral forward)
    sep = n("ShaderNodeSeparateColor", (-350, 0))
    lk(group_in.outputs["Color"], sep.inputs["Color"])

    combine = n("ShaderNodeCombineColor", (0, 0))
    combine.inputs["Blue"].default_value = 1.0
    lk(sep.outputs["Red"],        combine.inputs["Red"])
    lk(group_in.outputs["Alpha"], combine.inputs["Green"])

    nm = n("ShaderNodeNormalMap", (300, 0))
    lk(combine.outputs["Color"], nm.inputs["Color"])
    lk(nm.outputs["Normal"], group_out.inputs["Normal"])

    return g


def _setup_material_nodes(bl_mat, image_cache, diffuse_slot, bump_slot, opacity_slot):
    """
    Build a clean Principled BSDF material with textures wired correctly.
    Compatible with Blender 4.x and 5.x.
    """
    bl_mat.use_nodes = True
    bl_mat.blend_method = "CLIP"
    nodes = bl_mat.node_tree.nodes
    links = bl_mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    diffuse_img = image_cache.get(diffuse_slot)
    if diffuse_img:
        diff = nodes.new("ShaderNodeTexImage")
        diff.image = diffuse_img
        diff.location = (-200, 250)
        links.new(diff.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(diff.outputs["Alpha"], bsdf.inputs["Alpha"])

    bump_img = image_cache.get(bump_slot) if bump_slot >= 0 else None
    if bump_img:
        bump = nodes.new("ShaderNodeTexImage")
        bump.image = bump_img
        bump.image.colorspace_settings.name = "Non-Color"
        bump.location = (-500, -150)

        ng = _get_or_create_normal_group()
        nm_group = nodes.new("ShaderNodeGroup")
        nm_group.node_tree = ng
        nm_group.label = "RE4 UHD Normal"
        nm_group.location = (-100, -150)

        links.new(bump.outputs["Color"], nm_group.inputs["Color"])
        links.new(bump.outputs["Alpha"], nm_group.inputs["Alpha"])
        links.new(nm_group.outputs["Normal"], bsdf.inputs["Normal"])
