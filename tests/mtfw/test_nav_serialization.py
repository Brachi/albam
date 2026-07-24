import pytest


def test_export_header(nav_imported, nav_exported):
    snav = nav_imported
    dnav = nav_exported
    assert snav.indent == dnav.indent
    assert snav.version == dnav.version
    assert snav.reserved == dnav.reserved
    assert snav.num_vertices == dnav.num_vertices
    assert snav.num_faces == dnav.num_faces


def test_export_vertices(nav_imported, nav_exported):
    svtxs = nav_imported.vertices
    dvtxs = nav_exported.vertices
    for svtx, dvtx in zip(svtxs, dvtxs):
        assert svtx.x == pytest.approx(dvtx.x, rel=0.001)
        assert svtx.y == pytest.approx(dvtx.y, rel=0.001)
        assert svtx.z == pytest.approx(dvtx.z, rel=0.001)


def test_export_faces(nav_imported, nav_exported):
    sfaces = nav_imported.faces
    dfaces = nav_exported.faces
    for sface, dface in zip(sfaces, dfaces):
        assert sface.index == dface.index
        assert sface.unk_00 == dface.unk_00
        assert sface.flags == dface.flags
        assert sface.vertex_per_face == dface.vertex_per_face
        assert sface.v1 == dface.v1
        assert sface.v2 == dface.v2
        assert sface.v3 == dface.v3
        assert sface.num_neighbors == dface.num_neighbors
        sface_idxs = {}
        dface_idxs = {}
        for snrg, dnrg in zip(sface.neighbors, dface.neighbors):
            sface_idxs[snrg.face_index] = (snrg.edge, snrg.centroid_distance)
            dface_idxs[dnrg.face_index] = (dnrg.edge, dnrg.centroid_distance)
            assert snrg.padding == dnrg.padding
        for k, sv in sface_idxs.items():
            assert k in dface_idxs.keys()
            dv = dface_idxs[k]
            assert sv[0] == dv[0]
            assert sv[1] == pytest.approx(dv[1], rel=0.001)


def test_export_grid_header(nav_imported, nav_exported):
    sgridh = nav_imported
    dgridh = nav_exported
    sgridh.bbox.padding_00 == dgridh.bbox.padding_00
    sgridh.bbox.lower.x == pytest.approx(dgridh.bbox.lower.x, rel=0.001)
    sgridh.bbox.lower.y == pytest.approx(dgridh.bbox.lower.y, rel=0.001)
    sgridh.bbox.lower.z == pytest.approx(dgridh.bbox.lower.z, rel=0.001)
    sgridh.bbox.padding_01 == dgridh.bbox.padding_01
    sgridh.bbox.upper.x == pytest.approx(dgridh.bbox.upper.x, rel=0.001)
    sgridh.bbox.upper.y == pytest.approx(dgridh.bbox.upper.y, rel=0.001)
    sgridh.bbox.upper.z == pytest.approx(dgridh.bbox.upper.z, rel=0.001)
    sgridh.bbox.padding_02 == dgridh.bbox.padding_02
    sgridh.footer_indent == dgridh.footer_indent
    sgridh.footer_padding = dgridh.footer_padding


def test_export_grid(nav_imported, nav_exported):
    sgrid = nav_imported.lookup_grid
    dgrid = nav_exported.lookup_grid
    for scell, dcell in zip(sgrid, dgrid):
        scell.face_count = dcell.face_count
        sgfaces = scell.faces
        dgfaces = dcell.faces
        sface_idxs = set()
        dface_idxs = set()
        for sgface, dgface in zip(sgfaces, dgfaces):
            # assert sgface.face_index == dgface.face_index
            sface_idxs.add(sgface)
            dface_idxs.add(dgface)
            assert sgface.padding == dgface.padding
        # assert sface_idxs == dface_idxs
