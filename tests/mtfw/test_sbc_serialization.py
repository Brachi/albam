import pytest


def test_export_header(sbc_imported, sbc_exported):
    sbc_version = 255 if sbc_imported.header.indent == b"SBC\xFF" else 49
    sheader = sbc_imported.header
    dheader = sbc_exported.header
    assert sheader.indent == dheader.indent
    assert sheader.num_objects == dheader.num_objects
    assert sheader.num_faces == dheader.num_faces
    assert sheader.num_vertices == dheader.num_vertices
    if sbc_version == 49:
        assert sheader.version == dheader.version
    elif sbc_version == 255:
        assert sheader.unk_00 == dheader.unk_00
        assert sheader.num_stages == dheader.num_stages
        # assert sheader.num_pairs == dheader.num_pairs
    assert sheader.bounding_box.min[0] == pytest.approx(dheader.bounding_box.min[0], rel=0.001)
    assert sheader.bounding_box.min[1] == pytest.approx(dheader.bounding_box.min[1], rel=0.001)
    assert sheader.bounding_box.min[2] == pytest.approx(dheader.bounding_box.min[2], rel=0.001)
    assert sheader.bounding_box.max[0] == pytest.approx(dheader.bounding_box.max[0], rel=0.001)
    assert sheader.bounding_box.max[1] == pytest.approx(dheader.bounding_box.max[1], rel=0.001)
    assert sheader.bounding_box.max[2] == pytest.approx(dheader.bounding_box.max[2], rel=0.001)


def test_export_infos(sbc_imported, sbc_exported):
    sbc_version = 255 if sbc_imported.header.indent == b"SBC\xFF" else 49
    sinfos = sbc_imported.sbc_info
    dinfos = sbc_exported.sbc_info
    assert len(sinfos) == len(dinfos)
    for sinfo, dinfo in zip(sinfos, dinfos):
        if sbc_version == 255:
            assert sinfo.num_faces == dinfo.num_faces
            assert sinfo.num_vertices == dinfo.num_vertices
        assert sinfo.index_id == dinfo.index_id
        assert sinfo.bounding_box.min[0] == pytest.approx(dinfo.bounding_box.min[0], rel=0.001)
        assert sinfo.bounding_box.min[1] == pytest.approx(dinfo.bounding_box.min[1], rel=0.001)
        assert sinfo.bounding_box.min[2] == pytest.approx(dinfo.bounding_box.min[2], rel=0.001)
        assert sinfo.bounding_box.max[0] == pytest.approx(dinfo.bounding_box.max[0], rel=0.001)
        assert sinfo.bounding_box.max[1] == pytest.approx(dinfo.bounding_box.max[1], rel=0.001)
        assert sinfo.bounding_box.max[2] == pytest.approx(dinfo.bounding_box.max[2], rel=0.001)


def test_export_nodes(sbc_imported, sbc_exported):
    sbc_version = 255 if sbc_imported.header.indent == b"SBC\xFF" else 49
    if sbc_version == 255:
        sbvhc = sbc_imported.sbc_bvhc
        dbvhc = sbc_exported.sbc_bvhc
        for sbhv, dbvh in zip(sbvhc, dbvhc):
            assert sbhv.soh == dbvh.soh
            # assert sbhv.num_nodes == dbvh.num_nodes


def test_export_faces(sbc_imported, sbc_exported):
    sbc_version = 255 if sbc_imported.header.indent == b"SBC\xFF" else 49
    sfaces = sbc_imported.faces
    dfaces = sbc_exported.faces
    assert len(sfaces) == len(dfaces)
    for sface, dface in zip(sfaces, dfaces):
        assert sface.vert[0] == dface.vert[0]
        assert sface.vert[1] == dface.vert[1]
        assert sface.vert[2] == dface.vert[2]
        assert sface.type == dface.type
        if sbc_version == 49:
            assert sface.unk_00 == dface.unk_00  # probably junk
            assert sface.unk_01 == dface.unk_01  # probably junk
            assert sface.runtime_attr == dface.runtime_attr
            assert sface.special_attr == dface.special_attr  # 0 in re5
            assert sface.surface_attr == dface.surface_attr  # 0 in re5
        elif sbc_version == 255:
            assert sface.normal[0] == pytest.approx(dface.normal[0], rel=0.001)  # precsion error in re6
            assert sface.normal[1] == pytest.approx(dface.normal[1], rel=0.001)
            assert sface.normal[2] == pytest.approx(dface.normal[2], rel=0.001)
            # assert sface.adjacent[0] == dface.adjacent[0]
            # assert sface.adjacent[1] == dface.adjacent[1]
            # assert sface.adjacent[2] == dface.adjacent[2]


def test_export_vertices(sbc_imported, sbc_exported):
    sverts = sbc_imported.vertices
    dverts = sbc_exported.vertices
    assert len(sverts) == len(dverts)
    for svert, dvert in zip(sverts, dverts):
        assert svert.x == pytest.approx(dvert.x, rel=0.001)
        assert svert.y == pytest.approx(dvert.y, rel=0.001)
        assert svert.z == pytest.approx(dvert.z, rel=0.001)
