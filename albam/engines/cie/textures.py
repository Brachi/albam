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
import bpy
from .structs.tpl import Tpl


def _process_tpls(vfile_bin, root_id):
    # Process TPLs in a scope of the container with BIN file
    # print(f"Processing TPLs for root_id: {root_id}")
    vf_list = bpy.context.scene.albam.vfs.file_list
    #tpl_vfiles = [vf for vf in vf_list if vf.tree_node.root_id ==
    #              root_id and vf.display_name.endswith(".TPL")]
    tpl_vfiles = [vf for vf in vf_list if vf.name == root_id]
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
    vfile = tpl["vfile"]
    bl_image = bpy.data.images.get(vfile.display_name)
    if bl_image:
        return bl_image

    tex = vfile.get_bytes()

    bl_image = bpy.data.images.new(f"{vfile.display_name}", tpl["width"], tpl["height"])
    bl_image.source = "FILE"
    bl_image.pack(data=tex, data_len=len(tex))
    return bl_image
