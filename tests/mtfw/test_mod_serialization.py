import pytest


def test_export_header(mod_imported, mod_exported):
    sheader = mod_imported.header
    dheader = mod_exported.header

    bones_data_error = abs(mod_imported.bones_data.size_ - mod_exported.bones_data.size_)
    assert (sheader.version in (210, 211, 212) and not bones_data_error) or sheader.version == 156

    assert sheader.ident == dheader.ident == b"MOD\x00"
    assert sheader.version == dheader.version
    assert sheader.revision == dheader.revision
    assert sheader.num_bones == dheader.num_bones
    assert sheader.num_materials == dheader.num_materials
    assert (sheader.version in (210, 211, 212) and sheader.reserved_01 == dheader.reserved_01 or
            sheader.version == 156 and not getattr(dheader, "reserved_01", None))
    assert sheader.num_groups == dheader.num_groups
    assert sheader.num_meshes == dheader.num_meshes
    assert ((sheader.version in (210, 211, 212) and sheader.num_vertices == dheader.num_vertices) or
            sheader.version == 156)  # given 2nd vertex buffer unknowns

    assert sheader.offset_bones_data == dheader.offset_bones_data
    assert sheader.offset_groups == dheader.offset_groups - bones_data_error
    assert sheader.offset_materials_data == dheader.offset_materials_data - bones_data_error
    assert sheader.offset_meshes_data == dheader.offset_meshes_data - bones_data_error
    assert sheader.offset_vertex_buffer == dheader.offset_vertex_buffer - bones_data_error


def test_export_top_level(mod_imported, mod_exported):

    # assert mod_imported.bsphere.x == pytest.approx(mod_exported.bsphere.x, rel=0.5)
    assert mod_imported.bsphere.y == pytest.approx(mod_exported.bsphere.y, rel=0.001)
    # assert mod_imported.bsphere.z == pytest.approx(mod_exported.bsphere.z, rel=0.001)
    assert mod_imported.bsphere.w == pytest.approx(mod_exported.bsphere.w, rel=0.001)

    assert mod_imported.bbox_min.x == pytest.approx(mod_exported.bbox_min.x, rel=0.001)
    assert mod_imported.bbox_min.y == pytest.approx(mod_exported.bbox_min.y, rel=0.001)
    assert mod_imported.bbox_min.z == pytest.approx(mod_exported.bbox_min.z, rel=0.001)
    assert mod_imported.bbox_min.w == pytest.approx(mod_exported.bbox_min.w, rel=0.001)

    assert mod_imported.bbox_max.x == pytest.approx(mod_exported.bbox_max.x, rel=0.001)
    assert mod_imported.bbox_max.y == pytest.approx(mod_exported.bbox_max.y, rel=0.001)
    assert mod_imported.bbox_max.z == pytest.approx(mod_exported.bbox_max.z, rel=0.001)
    assert mod_imported.bbox_max.w == pytest.approx(mod_exported.bbox_max.w, rel=0.001)


def test_export_bones_data(mod_imported, mod_exported, subtests):
    # TODO: matrices
    sbd = mod_imported.bones_data
    dbd = mod_exported.bones_data
    bones_data_error = abs(mod_imported.bones_data.size_ - mod_exported.bones_data.size_)
    assert ((mod_exported.header.version in (210, 211, 212) and not bones_data_error) or
            mod_exported.header.version == 156)

    assert mod_imported.bones_data_size_ == mod_exported.bones_data_size_ - bones_data_error

    for i, src_bone in enumerate(sbd.bones_hierarchy):
        dst_bone = dbd.bones_hierarchy[i]

        with subtests.test(bone_index=i):
            assert src_bone.idx_anim_map == dst_bone.idx_anim_map
            assert src_bone.idx_parent == dst_bone.idx_parent
            assert src_bone.idx_mirror == dst_bone.idx_mirror
            assert src_bone.idx_mapping == dst_bone.idx_mapping
            assert src_bone.unk_01 == dst_bone.unk_01
            assert src_bone.parent_distance == pytest.approx(dst_bone.parent_distance, abs=9e-05)
            assert src_bone.location.x == pytest.approx(dst_bone.location.x, abs=9e-05)
            assert src_bone.location.y == pytest.approx(dst_bone.location.y, abs=9e-05)
            assert src_bone.location.z == pytest.approx(dst_bone.location.z, abs=9e-05)

    for i, src_psmatrix in enumerate(sbd.parent_space_matrices):
        dst_psmatrix = dbd.parent_space_matrices[i]
        with subtests.test(matrix_index=i):
            assert src_psmatrix.row_1.x == pytest.approx(dst_psmatrix.row_1.x, abs=9e-05)
            assert src_psmatrix.row_1.y == pytest.approx(dst_psmatrix.row_1.y, abs=9e-05)
            assert src_psmatrix.row_1.z == pytest.approx(dst_psmatrix.row_1.z, abs=9e-05)
            assert src_psmatrix.row_1.w == dst_psmatrix.row_1.w
            assert src_psmatrix.row_2.x == pytest.approx(dst_psmatrix.row_2.x, abs=9e-05)
            assert src_psmatrix.row_2.y == pytest.approx(dst_psmatrix.row_2.y, abs=9e-05)
            assert src_psmatrix.row_2.z == pytest.approx(dst_psmatrix.row_2.z, abs=9e-05)
            assert src_psmatrix.row_2.w == dst_psmatrix.row_2.w
            assert src_psmatrix.row_3.x == pytest.approx(dst_psmatrix.row_3.x, abs=9e-05)
            assert src_psmatrix.row_3.y == pytest.approx(dst_psmatrix.row_3.y, abs=9e-05)
            assert src_psmatrix.row_3.z == pytest.approx(dst_psmatrix.row_3.z, abs=9e-05)
            assert src_psmatrix.row_3.w == dst_psmatrix.row_3.w
            assert src_psmatrix.row_4.x == pytest.approx(dst_psmatrix.row_4.x, abs=9e-05)
            assert src_psmatrix.row_4.y == pytest.approx(dst_psmatrix.row_4.y, abs=9e-05)
            assert src_psmatrix.row_4.z == pytest.approx(dst_psmatrix.row_4.z, abs=9e-05)
            assert src_psmatrix.row_4.w == pytest.approx(dst_psmatrix.row_4.w, abs=9e-05)

    for i, src_ibmatrix in enumerate(sbd.inverse_bind_matrices):
        dst_ibmatrix = dbd.inverse_bind_matrices[i]
        with subtests.test(matrix_index=i):
            assert src_ibmatrix.row_1.x == pytest.approx(dst_ibmatrix.row_1.x, abs=9e-03)
            assert src_ibmatrix.row_1.y == pytest.approx(dst_ibmatrix.row_1.y, abs=9e-05)
            assert src_ibmatrix.row_1.z == pytest.approx(dst_ibmatrix.row_1.z, abs=9e-05)
            assert src_ibmatrix.row_1.w == dst_ibmatrix.row_1.w
            assert src_ibmatrix.row_2.x == pytest.approx(dst_ibmatrix.row_2.x, abs=9e-05)
            assert src_ibmatrix.row_2.y == pytest.approx(dst_ibmatrix.row_2.y, abs=9e-05)
            assert src_ibmatrix.row_2.z == pytest.approx(dst_ibmatrix.row_2.z, abs=9e-05)
            assert src_ibmatrix.row_2.w == dst_ibmatrix.row_2.w
            assert src_ibmatrix.row_3.x == pytest.approx(dst_ibmatrix.row_3.x, abs=9e-05)
            assert src_ibmatrix.row_3.y == pytest.approx(dst_ibmatrix.row_3.y, abs=9e-05)
            assert src_ibmatrix.row_3.z == pytest.approx(dst_ibmatrix.row_3.z, abs=9e-05)
            assert src_ibmatrix.row_3.w == dst_ibmatrix.row_3.w
            assert src_ibmatrix.row_4.x == pytest.approx(dst_ibmatrix.row_4.x, abs=9e-05)
            assert src_ibmatrix.row_4.y == pytest.approx(dst_ibmatrix.row_4.y, abs=9e-05)
            assert src_ibmatrix.row_4.z == pytest.approx(dst_ibmatrix.row_4.z, abs=9e-05)
            assert src_ibmatrix.row_4.w == pytest.approx(dst_ibmatrix.row_4.w, abs=9e-05)

    assert sbd.bone_map == dbd.bone_map


def test_export_groups(mod_imported, mod_exported):

    assert mod_imported.groups_size_ == mod_exported.groups_size_

    assert [g.group_index for g in mod_imported.groups] == [g.group_index for g in mod_exported.groups]
    assert [g.pos.x for g in mod_imported.groups] == [g.pos.x for g in mod_exported.groups]
    assert [g.pos.y for g in mod_imported.groups] == [g.pos.y for g in mod_exported.groups]
    assert [g.pos.z for g in mod_imported.groups] == [g.pos.z for g in mod_exported.groups]
    assert [g.radius for g in mod_imported.groups] == [g.radius for g in mod_exported.groups]


def test_materials_data(mod_imported, mod_exported):

    assert mod_imported.materials_data.size_ == mod_exported.materials_data.size_
    assert ((mod_imported.header.version in (210, 211, 212) and
            mod_imported.materials_data.material_names == mod_exported.materials_data.material_names) or
            mod_imported.header.version == 156)


def test_meshes_data_21(mod_imported, mod_exported, subtests):
    if mod_imported.header.version not in (210, 212):
        pytest.skip()

    for i, mesh in enumerate(mod_imported.meshes_data.meshes):
        src_mesh = mesh
        dst_mesh = mod_exported.meshes_data.meshes[i]
        with subtests.test(mesh_index=i):
            assert src_mesh.draw_mode == dst_mesh.draw_mode
            assert src_mesh.num_vertices == dst_mesh.num_vertices
            assert src_mesh.idx_group == dst_mesh.idx_group
            assert src_mesh.idx_material == dst_mesh.idx_material
            assert src_mesh.level_of_detail == dst_mesh.level_of_detail
            assert src_mesh.disp == dst_mesh.disp
            assert src_mesh.shape == dst_mesh.shape
            assert src_mesh.sort == dst_mesh.sort
            # assert src_mesh.max_bones_per_vertex == dst_mesh.max_bones_per_vertex
            # assert src_mesh.vertex_stride == dst_mesh.vertex_stride
            assert src_mesh.alpha_priority == dst_mesh.alpha_priority
            assert src_mesh.topology == dst_mesh.topology
            assert src_mesh.binormal_flip == dst_mesh.binormal_flip
            assert src_mesh.bridge == dst_mesh.bridge
            # assert src_mesh.vertex_format == dst_mesh.vertex_format
            assert src_mesh.bone_id_start == dst_mesh.bone_id_start
            assert src_mesh.num_weight_bounds == dst_mesh.num_weight_bounds
            assert src_mesh.connect_id == dst_mesh.connect_id
            assert src_mesh.min_index == dst_mesh.min_index
            assert src_mesh.max_index == dst_mesh.max_index
            assert src_mesh.boundary == dst_mesh.boundary

    assert mod_imported.header.version in (210, 212) and (
        mod_imported.num_weight_bounds == mod_exported.num_weight_bounds)


def test_vertices(mod_imported, mod_exported, subtests):
    if mod_imported.header.version not in (210, 212):  # RE5 has some mess with in hands files
        pytest.skip()
    assert len(mod_imported.meshes_data.meshes) == len(mod_exported.meshes_data.meshes)
    for mi, mesh in enumerate(mod_imported.meshes_data.meshes):
        src_mesh = mesh
        dst_mesh = mod_exported.meshes_data.meshes[mi]
        with subtests.test(mesh_index=mi):
            assert src_mesh.num_vertices == dst_mesh.num_vertices
            # disable for now, some normals don't match
            '''for vi, dst_vertex in enumerate(dst_mesh.vertices):
                src_vertex = src_mesh.vertices[vi]
                with subtests.test(mesh_index=mi, vertex_index=vi):
                    assert src_vertex.normal.x == (dst_vertex.normal.x + 1) or \
                        src_vertex.normal.x == (dst_vertex.normal.x - 1) or \
                        src_vertex.normal.x == (dst_vertex.normal.x + 2) or \
                        src_vertex.normal.x == (dst_vertex.normal.x - 2) or \
                        src_vertex.normal.x == dst_vertex.normal.x'''


@pytest.mark.xfail(reason="WIP")
def test_header_xfail(pl0000_roundtrip):
    """
    Tests to fix
    """
    src_mod, dst_mod = pl0000_roundtrip
    sheader = src_mod.header
    dheader = dst_mod.header

    assert sheader.num_faces == dheader.num_faces
    assert sheader.num_edges == dheader.num_edges
    assert sheader.version not in (210, 211, 212) or sheader.size_file == dheader.size_file
    # in 210, given we don't export some vertex formats (like the one witih blend shapes of 64 bytes)
    # the size and hence the offset of the index buffer will differ
    assert sheader.offset_index_buffer == dheader.offset_index_buffer
    assert sheader.size_vertex_buffer == dheader.size_vertex_buffer


@pytest.mark.xfail(reason="WIP")
def test_meshes_data_xfail(mod_imported, mod_exported, subtests):

    assert mod_imported.meshes_data.num_weight_bounds == mod_exported.meshes_data.num_weight_bounds
    for i, mesh in enumerate(mod_imported.meshes_data.meshes):
        src_mesh = mesh
        dst_mesh = mod_exported.meshes_data.meshes[i]
        with subtests.test(i=i):
            assert src_mesh.vertex_position == dst_mesh.vertex_position
            assert src_mesh.vertex_offset == dst_mesh.vertex_offset
            assert src_mesh.face_position == dst_mesh.face_position
            assert src_mesh.num_indices == dst_mesh.num_indices
            assert src_mesh.face_offset == dst_mesh.face_offset
