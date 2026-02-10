import pytest


def test_export_header(sbc_imported, sbc_exported):
    sbc_version = 255 if sbc_imported.header.magic == b"SBC\xFF" else 49
    sheader = sbc_imported.header
    dheader = sbc_exported.header
    assert sheader.magic == dheader.magic
    if sbc_version == 49:
        assert sheader.version == dheader.version
        assert sheader.num_groups == dheader.num_groups
        assert sheader.num_faces == dheader.num_faces
        assert sheader.num_vertices == dheader.num_vertices
    assert sheader.bbox.min.x == pytest.approx(dheader.bbox.min.x, rel=0.001)
    assert sheader.bbox.min.y == pytest.approx(dheader.bbox.min.y, rel=0.001)
    assert sheader.bbox.min.z == pytest.approx(dheader.bbox.min.z, rel=0.001)
    assert sheader.bbox.max.x == pytest.approx(dheader.bbox.max.x, rel=0.001)
    assert sheader.bbox.max.y == pytest.approx(dheader.bbox.max.y, rel=0.001)
    assert sheader.bbox.max.z == pytest.approx(dheader.bbox.max.z, rel=0.001)


def test_export_infos(sbc_imported, sbc_exported):
    sinfos = sbc_imported.sbc_info
    dinfos = sbc_exported.sbc_info
    assert len(sinfos) == len(dinfos)
    for sinfo, dinfo in zip(sinfos, dinfos):
        assert sinfo.group_id == dinfo.group_id
        assert sinfo.bounding_box.min.x == pytest.approx(dinfo.bounding_box.min.x, rel=0.001)
        assert sinfo.bounding_box.min.y == pytest.approx(dinfo.bounding_box.min.y, rel=0.001)
        assert sinfo.bounding_box.min.z == pytest.approx(dinfo.bounding_box.min.z, rel=0.001)
        assert sinfo.bounding_box.max.x == pytest.approx(dinfo.bounding_box.max.x, rel=0.001)
        assert sinfo.bounding_box.max.y == pytest.approx(dinfo.bounding_box.max.y, rel=0.001)
        assert sinfo.bounding_box.max.z == pytest.approx(dinfo.bounding_box.max.z, rel=0.001)


def test_export_faces(sbc_imported, sbc_exported):
    sbc_version = 255 if sbc_imported.header.magic == b"SBC\xFF" else 49
    sfaces = sbc_imported.faces
    dfaces = sbc_exported.faces
    assert len(sfaces) == len(dfaces)
    for sface, dface in zip(sfaces, dfaces):
        assert sface.vert[0] == dface.vert[0]
        assert sface.vert[1] == dface.vert[1]
        assert sface.vert[2] == dface.vert[2]
        if sbc_version == 49:
            assert sface.unk_00 == dface.unk_00  # probably junk
            assert sface.unk_01 == dface.unk_01  # probably junk
            assert sface.runtime_attr == dface.runtime_attr
            assert sface.type == dface.type
            assert sface.special_attr == dface.special_attr  # 0 in re5
            assert sface.surface_attr == dface.surface_attr  # 0 in re5


def test_export_vertices(sbc_imported, sbc_exported):
    sverts = sbc_imported.vertices
    dverts = sbc_exported.vertices
    assert len(sverts) == len(dverts)
    for svert, dvert in zip(sverts, dverts):
        assert svert.x == pytest.approx(dvert.x, rel=0.001)
        assert svert.y == pytest.approx(dvert.y, rel=0.001)
        assert svert.z == pytest.approx(dvert.z, rel=0.001)
