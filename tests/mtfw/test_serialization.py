# import io
import os

import bpy
import pytest
# from kaitaistruct import KaitaiStream

from .conftest import FileWrapper
from albam.blender_ui.import_panel import ALBAM_OT_Import
from albam.vfs import ALBAM_OT_VirtualFileSystemBlenderAddFiles

from albam.engines.mtfw.mesh import export_mod, APPID_CLASS_MAPPER


def test_export(arc_file):
    arc_filepath = arc_file["filepath"]
    app_id = arc_file["app_id"]
    directory = os.path.dirname(arc_filepath)
    arc_name = os.path.basename(arc_filepath)
    vfs = bpy.context.scene.albam.vfs
    file_list = vfs.file_list
    vfs.app_selected = app_id

    ALBAM_OT_VirtualFileSystemBlenderAddFiles._execute(bpy.context, directory, [FileWrapper(arc_filepath)])
    mod_files = sorted(
        [f for f in file_list if f.name.endswith('.mod') and arc_name in f.tree_node.root_id],
        key=lambda k: k.name
    )
    if mod_files:
        mod_file = mod_files[0]  # XXX temp testing only first modfile in arc
    else:
        pytest.skip()
    ALBAM_OT_Import._execute(mod_file, bpy.context)
    exportables = [
        f for f in bpy.context.scene.albam.exportable.file_list
        if f.bl_object.albam_asset.relative_path == mod_file.relative_path
    ]
    vfiles = export_mod(exportables[0].bl_object)
    mod_vfiles = [vf for vf in vfiles if vf.relative_path == mod_file.relative_path]
    mod_vfile = mod_vfiles[0]
    mod_bytes = mod_vfile.data_bytes

    assert len(mod_vfiles) == 1
    Mod = APPID_CLASS_MAPPER[app_id]
    src_mod = Mod.from_bytes(mod_file.get_bytes())
    dst_mod = Mod.from_bytes(mod_bytes)
    src_mod._read()
    dst_mod._read()

    # skipping for now until finding right threshold
    # assert src_mod.bbox_min.x == pytest.approx(dst_mod.bbox_min.x)
    # assert src_mod.bbox_min.y == pytest.approx(dst_mod.bbox_min.y)
    # assert src_mod.bbox_min.z == pytest.approx(dst_mod.bbox_min.z)
    # assert src_mod.bbox_min.w == pytest.approx(dst_mod.bbox_min.w)
    # assert src_mod.bbox_max.x == pytest.approx(dst_mod.bbox_max.x, rel=8.8e-05)
    # assert src_mod.bbox_max.y == pytest.approx(dst_mod.bbox_max.y, rel=0.8e-05)
    # assert src_mod.bbox_max.z == pytest.approx(dst_mod.bbox_max.z, rel=4.0e-04)
    # assert src_mod.bbox_max.w == pytest.approx(dst_mod.bbox_max.w, rel=4.0e-04)

    # bones
    assert src_mod.header.num_bones == dst_mod.header.num_bones
    if dst_mod.header.num_bones:
        assert (
            (src_mod.header.version == 156 and
             src_mod.header.num_bone_palettes != dst_mod.header.num_bone_palettes
             ) or
            src_mod.bones_data.size_ == dst_mod.bones_data.size_
        )
        # Bbox re-calculation changes the stream (float precision lost)
        # TODO: redo these tests
        # src_stream = KaitaiStream(io.BytesIO(bytearray(src_mod.bones_data.size_)))
        # dst_stream = KaitaiStream(io.BytesIO(bytearray(dst_mod.bones_data.size_)))
        # src_mod.bones_data._write(src_stream)
        # dst_mod.bones_data._write(dst_stream)
        # bone-palettes are non-deterministic so far, so the bytes will be different only in that part
        # assert dst_mod.header.version == 156 or src_stream.to_byte_array() == dst_stream.to_byte_array()
    # groups
    # Can't compare bytes, per unreliable float conversion
    assert src_mod.header.num_groups == dst_mod.header.num_groups
    # weight-bounds
    # Disabling due to LODS hardcoded
    # assert (
    #    (src_mod.header.version == 156 and
    #        src_mod.meshes_data.num_weight_bounds == dst_mod.meshes_data.num_weight_bounds) or
    #    (src_mod.header.version == 210 and
    #     src_mod.num_weight_bounds == dst_mod.num_weight_bounds)
    # )
