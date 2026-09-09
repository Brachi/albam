"""
Round-trip a real RE4UHD model through the import and export functions:
import it, export it, import what came out, and check the model survived.

Unlike tests/cie/test_lfs_fs.py, which only reads, this drives the registry,
the VFS and the material and armature building the way an actual import and
export do - so it covers the parts a parsing test cannot reach.

What is compared, and what deliberately is not: triangles, materials and
bones have to match exactly, and so do every material's texture slots.
Vertex counts do not: corners are shared along a strip but never across a UV
seam or a shading split, and a strip restart rewrites the two corners it
begins with, so a re-imported model carries slightly more vertices while
describing the same surface (see albam/engines/cie/mesh.py).
"""
import json
import os

import bpy
import pytest

from albam.lib import fs_registry
from tests.conftest import close_new_fs_roots, remove_new_vfs_roots, vfs_root_names
from tests.cie.lfs_paths import resolve_archive_hashes

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")
DATASET_PATH = os.path.join(DATASETS_DIR, "bin_serialization_hashes.json")
with open(DATASET_PATH) as f:
    BIN_SERIALIZATION_DATASET = json.load(f)

MESH_FLAG_OFFSET = 0x20
MESH_FLAG = 0x80000000


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_archive_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_archive_path_hash")
        argvalues = [(d["app_id"], d["archive_path_hash"]) for d in BIN_SERIALIZATION_DATASET]
        ids = [f"{d['app_id']}-{d['archive_path_hash']}" for d in BIN_SERIALIZATION_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def test_dataset_hashes_are_in_catalog():
    """No plaintext game asset path is ever committed - see
    tests/cie/test_lfs_fs.py, same check. CI-safe."""
    for entry in BIN_SERIALIZATION_DATASET:
        catalog_path = os.path.join(DATASETS_DIR, f"{entry['app_id']}_catalog.json")
        with open(catalog_path) as f:
            catalog = {e["path_hash"]: e for e in json.load(f)}
        assert entry["archive_path_hash"] in catalog, (
            f"{entry['archive_path_hash']!r} is not in {catalog_path!r}"
        )


@pytest.fixture
def _clean_scene():
    # vfs, exported and bpy.data are session-scoped state: register() runs
    # once per pytest session, so a test that leaves objects or roots behind
    # changes what the next one sees.
    before = fs_registry.keys()
    before_roots = vfs_root_names()
    yield
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    remove_new_vfs_roots(before_roots)
    bpy.context.scene.albam.exported.file_list.clear()
    close_new_fs_roots(before)


def _is_mesh_bin(data):
    if len(data) < MESH_FLAG_OFFSET + 4:
        return False
    return bool(int.from_bytes(
        data[MESH_FLAG_OFFSET:MESH_FLAG_OFFSET + 4], "little") & MESH_FLAG)


def _model_state(bl_object):
    """What has to survive a round trip.

    Vertex count is deliberately not part of this: it is only ever compared
    between two re-imports (see the module docstring), where a strip restart
    legitimately adds corners without changing the surface. Whether the
    geometry itself - positions, normals, UVs - actually matches the shipped
    file is test_bin_round_trip_matches_the_original_geometry's job, which
    compares against the original bytes instead.
    """
    meshes = [o for o in bl_object.children_recursive if o.type == "MESH"]
    if bl_object.type == "MESH":
        meshes.append(bl_object)
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    materials = [slot.material for o in meshes for slot in o.material_slots if slot.material]
    return {
        "triangles": sum(len(polygon.vertices) - 2
                         for o in meshes for polygon in o.data.polygons),
        "materials": len(materials),
        "bones": len(armatures[0].data.bones) if armatures else 0,
    }


def _decoded_triangles(bin_bytes):
    """Every triangle `bin_bytes` describes, as a multiset of
    ((position, uv), normal) corners - decoded straight off the file's own
    bytes through the same per-corner arrays and strip-to-triangle logic
    import uses (see albam.engines.cie.mesh), not through Blender.

    Every value is kept exactly as the file states it; what absorbs the
    float32 round trip is the tolerance the triangles are matched within
    (see _match_triangles), not any rounding done here. The normal is kept
    alongside each corner rather than folded into the surface it belongs to:
    Blender recomputes a loop's split normal from the surrounding topology on
    every mesh edit, and reproduces it only to within about a tenth even for
    a model that came back with the same surface - see
    test_bin_round_trip_matches_the_original_geometry, which checks normals
    on their own with a looser, majority-agreement tolerance instead of
    demanding every one match.

    Corners are kept in the order the file gives them; the comparison itself
    is order-independent and winding-independent (see _shape) because a
    no-edit re-export is free to walk materials and strips in a different
    corner order and still describe the same surface - triangle count is what
    has to match exactly, not corner order or count (see the module
    docstring).
    """
    from albam.engines.cie.mesh import _build_faces, _decode_normal, _yz_flip
    from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

    parsed = Re4UhdBin.from_bytes(bin_bytes)
    parsed._read()
    faces, _mat_face_ranges = _build_faces(parsed)

    positions = [_yz_flip(v.x, v.y, v.z) for v in parsed.vertex_positions]
    normals = [_decode_normal(n) for n in parsed.normals] if parsed.normals else None
    uvs = [(uv.u, 1.0 - uv.v) for uv in parsed.texcoords] if parsed.texcoords else None

    def corner(i):
        uv = tuple(uvs[i]) if uvs else ()
        normal = tuple(normals[i]) if normals else ()
        return (tuple(positions[i]), uv), normal

    return [tuple(corner(i) for i in triangle) for triangle in faces]


# A coordinate makes a float32 -> double -> float32 round trip on the way
# through Blender and comes back a few ulps off, so nothing here is compared
# for equality. These are the absolute tolerances a corner is matched
# within - one raw unit of whatever the file itself stores, which is orders
# of magnitude tighter than any scale, axis or UV regression and wide enough
# that no value sits on a boundary where the round trip decides the answer.
POSITION_TOLERANCE = 0.001
UV_TOLERANCE = 0.0001
NORMAL_TOLERANCE = 0.15


def _shape(triangle):
    """A triangle's surface: its corner positions and UVs, sorted.

    Sorted so that which corner the file listed first never decides a match -
    a re-export is free to state the same triangle from a different corner or
    in the opposite winding.
    """
    return tuple(sorted(position + uv for position, uv in
                        (corner for corner, _normal in triangle)))


def _same_surface(one, other):
    """Whether two surfaces (see _shape) are the same one within tolerance."""
    if len(one) != len(other):
        return False
    for corner, other_corner in zip(one, other):
        if len(corner) != len(other_corner):
            return False
        for i, (value, other_value) in enumerate(zip(corner, other_corner)):
            tolerance = POSITION_TOLERANCE if i < 3 else UV_TOLERANCE
            if abs(value - other_value) > tolerance:
                return False
    return True


def _match_triangles(original_triangles, exported_triangles):
    """Pair each original triangle with the exported triangle describing the
    same surface, as (pairs, originals nothing matched).

    Both sides are sorted by surface and walked together, so a pair costs a
    sort rather than a scan. Nothing is snapped to a grid on the way: a
    quantized coordinate landing on a cell boundary - an exact half raw unit,
    which axis-aligned or tool-quantized geometry produces readily - is
    exactly the value an exact-key comparison cannot survive, since the round
    trip alone decides which side of the boundary it lands on.
    """
    original = sorted((_shape(t), t) for t in original_triangles)
    exported = sorted((_shape(t), t) for t in exported_triangles)

    pairs = []
    unmatched = []
    i = j = 0
    while i < len(original) and j < len(exported):
        if _same_surface(original[i][0], exported[j][0]):
            pairs.append((original[i][1], exported[j][1]))
            i += 1
            j += 1
        elif original[i][0] < exported[j][0]:
            unmatched.append(original[i][1])
            i += 1
        else:
            j += 1
    unmatched.extend(triangle for _surface, triangle in original[i:])
    return pairs, unmatched


def _normal_agreement(pairs):
    """The fraction of matched triangles (see _match_triangles) that also
    carry the normals they shipped with.

    Every triangle here already describes the surface it shipped with; this
    measures how many also kept its normals, which - unlike the surface -
    Blender does not reproduce on every triangle even for a model with no
    real regression (see _decoded_triangles).
    """
    if not pairs:
        return 0.0

    def normals(triangle):
        return [normal for _corner, normal in sorted(triangle, key=lambda c: c[0])]

    agreed = 0
    for original, exported in pairs:
        if all(abs(a - b) <= NORMAL_TOLERANCE
               for original_normal, exported_normal in zip(normals(original),
                                                           normals(exported))
               for a, b in zip(original_normal, exported_normal)):
            agreed += 1
    return agreed / len(pairs)


def _texture_slots(bin_bytes):
    """Every material's texture indices, as the file stores them."""
    from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

    parsed = Re4UhdBin.from_bytes(bin_bytes)
    parsed._read()
    return [(m.diffuse_map, m.bump_map, m.opacity_map,
             m.generic_specular_map, m.custom_specular_map, m.material_flag)
            for m in parsed.materials]


def test_bin_round_trips_through_export(game_root, local_app_id,
                                        local_archive_path_hash, _clean_scene):
    from albam.engines.cie.mesh import AUTO_TPL
    from albam.registry import blender_registry

    archive_path = resolve_archive_hashes(
        game_root, {local_archive_path_hash})[local_archive_path_hash]

    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = local_app_id
    root = vfs.add_real_file(local_app_id, archive_path)

    models = [vf for vf in vfs.file_list
              if vf.tree_node.root_id == root.name and not vf.is_root and
              vf.display_name.lower().endswith(".bin") and _is_mesh_bin(vf.get_bytes())]
    assert models, "this archive should hold a mesh .bin"
    vfile = models[0]

    import_function = blender_registry.import_registry[(local_app_id, "bin")]
    export_function = blender_registry.export_registry[(local_app_id, "bin")]

    vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL
    original_bytes = vfile.get_bytes()
    bl_object = import_function(vfile, bpy.context)
    before = _model_state(bl_object)
    assert before["triangles"] > 0

    bl_object.albam_asset.app_id = local_app_id
    bl_object.albam_asset.extension = "bin"
    bl_object.albam_asset.relative_path = vfile.display_name
    bl_object.albam_asset.original_bytes = original_bytes
    vfiles = export_function(bl_object)
    assert len(vfiles) == 1
    exported_bytes = vfiles[0].data_bytes
    assert _is_mesh_bin(exported_bytes), "the exported file should read as a mesh"

    # Texture slots are rebuilt from the material's image nodes rather than
    # carried, so they are worth checking on their own: getting them wrong
    # still produces a valid file, just an untextured one.
    assert _texture_slots(exported_bytes) == _texture_slots(original_bytes)

    exported_vfs = bpy.context.scene.albam.exported
    exported_vfs.add_export_root(local_app_id, "serialization-test", vfiles)
    reimported = next(vf for vf in exported_vfs.file_list
                      if not vf.is_root and vf.display_name == vfile.display_name)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    bl_object = import_function(reimported, bpy.context)
    after = _model_state(bl_object)

    assert after["triangles"] == before["triangles"]
    assert after["materials"] == before["materials"]
    assert after["bones"] == before["bones"]


def test_bin_round_trip_matches_the_original_geometry(
        game_root, local_app_id, local_archive_path_hash, _clean_scene):
    """A no-edit re-export describes the same surface the shipped file did.

    Every other geometry check in this module goes through a second import
    of albam's own output, which cannot catch a bug that is consistent with
    itself - a wrong scale, a flipped axis or a broken normal decoding would
    still come back looking right, since the same (wrong) math reads it back
    that wrote it. This instead decodes both files' raw per-corner arrays
    independently (see _decoded_triangles) and compares them directly, which
    is the only check here that touches the bytes the game actually shipped.
    """
    from albam.engines.cie.mesh import AUTO_TPL
    from albam.registry import blender_registry

    archive_path = resolve_archive_hashes(
        game_root, {local_archive_path_hash})[local_archive_path_hash]

    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = local_app_id
    root = vfs.add_real_file(local_app_id, archive_path)

    models = [vf for vf in vfs.file_list
              if vf.tree_node.root_id == root.name and not vf.is_root and
              vf.display_name.lower().endswith(".bin") and _is_mesh_bin(vf.get_bytes())]
    assert models, "this archive should hold a mesh .bin"
    vfile = models[0]

    import_function = blender_registry.import_registry[(local_app_id, "bin")]
    export_function = blender_registry.export_registry[(local_app_id, "bin")]

    vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL
    original_bytes = vfile.get_bytes()
    bl_object = import_function(vfile, bpy.context)

    bl_object.albam_asset.app_id = local_app_id
    bl_object.albam_asset.extension = "bin"
    bl_object.albam_asset.relative_path = vfile.display_name
    bl_object.albam_asset.original_bytes = original_bytes
    exported_bytes = export_function(bl_object)[0].data_bytes

    original_triangles = _decoded_triangles(original_bytes)
    exported_triangles = _decoded_triangles(exported_bytes)
    assert original_triangles, "this model should hold at least one triangle"

    # Strict: position and UV, decoded straight off the bytes on both sides.
    # This is what would catch a scale, axis or UV regression - the surface a
    # re-exported model describes has to be exactly the one it shipped with.
    assert len(exported_triangles) == len(original_triangles), (
        "the re-export does not describe as many triangles as the shipped file"
    )
    pairs, unmatched = _match_triangles(original_triangles, exported_triangles)
    assert not unmatched, (
        f"{len(unmatched)} of {len(original_triangles)} shipped triangles are not "
        f"described by the re-export, e.g. {_shape(unmatched[0])}"
    )

    # Loose: normals agree for the large majority of triangles rather than
    # all of them - see _decoded_triangles for why an exact-match normal
    # check would fail even a faithful re-export.
    agreement = _normal_agreement(pairs)
    assert agreement > 0.9, (
        f"only {agreement:.0%} of triangles kept the normals they shipped with"
    )


def test_importing_several_models_from_one_archive(game_root, local_app_id,
                                                   local_archive_path_hash, _clean_scene):
    """Importing model after model from one archive keeps working.

    The second one onward is where this broke: the first model in an archive
    brings in the armature and is represented by it, and the import operator
    leaves an armature alone because building one has already linked it. Every
    later model reuses that armature and so is represented by an empty
    instead, which the operator does link - and the importer had linked it
    too, which raises. Every model after the first failed with "already in
    collection" while its geometry had in fact been built.
    """
    from albam.engines.cie.mesh import AUTO_TPL

    archive_path = resolve_archive_hashes(
        game_root, {local_archive_path_hash})[local_archive_path_hash]

    vfs = bpy.context.scene.albam.vfs
    bpy.context.scene.albam.apps.app_selected = local_app_id
    root = vfs.add_real_file(local_app_id, archive_path)

    models = [vf for vf in vfs.file_list
              if vf.tree_node.root_id == root.name and not vf.is_root and
              vf.display_name.lower().endswith(".bin") and _is_mesh_bin(vf.get_bytes())]
    if len(models) < 2:
        pytest.skip("this archive holds a single model")

    bpy.context.scene.albam.import_options_bin.tpl_file_id = AUTO_TPL
    for vfile in models[:4]:
        vfs.file_list_selected_index = vfs.file_list.find(vfile.name)
        # Through the operator, not the import function: what broke lives in
        # the operator's own linking, so calling past it would not see it.
        result = bpy.ops.albam.import_vfile()
        assert result == {"FINISHED"}, f"{vfile.display_name} returned {result}"

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    assert len(meshes) >= len(models[:4]), "every imported model should be in the scene"
