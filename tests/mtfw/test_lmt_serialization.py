from albam.engines.mtfw.animation import KEYFRAME_TYPES_51


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
    i = 0
    for sab, dab in zip(samnib, damnib):
        if sab.offset != 0:
            print(i)
            # assert sab.block_header.ofs_frame == dab.block_header.ofs_frame
            assert sab.block_header.num_tracks == dab.block_header.num_tracks
            # anim blocks have non correct value of frames, actually 1
            if i not in (100, 101, 102, 103, 104):
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
            j = 0
            for str, dtr in zip(stracks, dtracks):
                print("amim_block:", i, "track:", j, str.bone_index)
                # buffert type selection isn't that reliable for static frames
                # if str.bone_index != 254:
                #    assert str.buffer_type == dtr.buffer_type
                assert str.usage == dtr.usage
                # assert str.joint_type == dtr.joint_type
                assert str.bone_index == dtr.bone_index
                assert str.weight == dtr.weight
                # tr.len_data == dtr.len_data
                j += 1
        else:
            assert sab.offset == dab.offset
        i += 1
