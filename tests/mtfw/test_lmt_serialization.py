
def test_export_header(lmt_imported, lmt_exported):
    slmt = lmt_imported
    dlmt = lmt_exported
    slmt.id_magic == dlmt.id_magic
    slmt.version == dlmt.version
    slmt.num_block_offsets == dlmt.num_block_offsets


def test_export_anim_block(lmt_imported, lmt_exported):
    slmt = lmt_imported
    dlmt = lmt_exported
    version = slmt.version
    samnib = [ab for _, ab in enumerate(slmt.block_offsets)]
    damnib = [ab for _, ab in enumerate(dlmt.block_offsets)]
    for sab, dab in zip(samnib, damnib):
        if sab.offset != 0:
            # assert sab.block_header.ofs_frame == dab.block_header.ofs_frame
            assert sab.block_header.num_tracks == dab.block_header.num_tracks
            assert sab.block_header.num_frames == dab.block_header.num_frames
            assert sab.block_header.loop_frame == dab.block_header.loop_frame
            assert sab.block_header.init_position == dab.block_header.init_position
            assert sab.block_header.init_quaterion == dab.block_header.init_quaterion
            stracks = [tr for _, tr in enumerate(sab.block_header.tracks)]
            dtracks = [tr for _, tr in enumerate(dab.block_header.tracks)]
            for strack in stracks:
                bone = strack.bone_index
                dbone = -1
                for dtrack in dtracks:
                    if dtrack.bone_index == bone:
                        dbone = dtrack.bone_index
                if dbone == -1:
                    print(bone)
            '''
            for str, dtr in zip(stracks, dtracks):
                str.buffer_type = dtr.buffer_type
                str.usage == dtr.usage
                str.joint_type == dtr.joint_type
                str.bone_index == dtr.bone_index
                str.weight == dtr.weight
                str.len_data == dtr.len_data'''
        else:
            assert sab.offset == dab.offset
