import pytest


def test_export_header(sbc_imported, sbc_exported):
    sheader = sbc_imported.header
    dheader = sbc_exported.header
    assert sheader.magic == dheader.magic
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
        assert sinfo.bbox_this.min.x == pytest.approx(dinfo.bbox_this.min.x, rel=0.001)
        assert sinfo.bbox_this.min.y == pytest.approx(dinfo.bbox_this.min.y, rel=0.001)
        assert sinfo.bbox_this.min.z == pytest.approx(dinfo.bbox_this.min.z, rel=0.001)
        assert sinfo.bbox_this.max.x == pytest.approx(dinfo.bbox_this.max.x, rel=0.001)
        assert sinfo.bbox_this.max.y == pytest.approx(dinfo.bbox_this.max.y, rel=0.001)
        assert sinfo.bbox_this.max.z == pytest.approx(dinfo.bbox_this.max.z, rel=0.001)


def test_export_faces(sbc_imported, sbc_exported):
    sfaces = sbc_imported.faces
    dfaces = sbc_exported.faces
    assert len(sfaces) == len(dfaces)
    for sface, dface in zip(sfaces, dfaces):
        assert sface.vert[0] == dface.vert[0]
        assert sface.vert[1] == dface.vert[1]
        assert sface.vert[2] == dface.vert[2]
        assert sface.runtime_attr == dface.runtime_attr
        assert sface.type == dface.type
        assert sface.special_attr == dface.special_attr
        assert sface.surface_attr == dface.surface_attr
