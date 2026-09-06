import json
import os

# Reuses test_edgemodel_parsing.py's own committed, catalog-verified dataset
# (see its test_dataset_hashes_are_in_catalog) - these 5 files already cover
# a range of real .matb materials (multiple texture slots, including at
# least one normal map each), which is exactly what this node-layout test
# needs; no new hashes required.
EDGEMODEL_PARSING_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "edgemodel_parsing_hashes.json")
with open(EDGEMODEL_PARSING_DATASET_PATH) as f:
    EDGEMODEL_PARSING_DATASET = json.load(f)

# Blender doesn't report a usable node.dimensions headlessly (it stays
# (0, 0) until the node has actually been drawn once, which never happens
# under pytest), so overlap-check with node.width (accurate, static) plus a
# fixed height estimate generous enough to cover an expanded image-preview
# thumbnail (an assigned ShaderNodeTexImage draws roughly as tall as it is
# wide, ~240px, plus its header) - real dimensions would only make an
# overlapping pair look bigger, never smaller, so this stays a safe
# (conservative) check.
_NODE_HEIGHT_ESTIMATE = 300.0


def pytest_generate_tests(metafunc):
    if ("local_app_id" in metafunc.fixturenames and
            "local_edgemodel_path_hash" in metafunc.fixturenames):
        argnames = ("local_app_id", "local_edgemodel_path_hash")
        argvalues = [(d["app_id"], d["edgemodel_path_hash"]) for d in EDGEMODEL_PARSING_DATASET]
        ids = [f"{d['app_id']}-{d['edgemodel_path_hash']}" for d in EDGEMODEL_PARSING_DATASET]
        metafunc.parametrize(argnames, argvalues, ids=ids, scope="session")


def _bbox(node):
    x, y = node.location
    w = node.width
    h = _NODE_HEIGHT_ESTIMATE
    return (x, x + w, y - h, y)


def _overlaps(a, b):
    ax0, ax1, ay0, ay1 = a
    bx0, bx1, by0, by1 = b
    return ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1


def test_material_node_layout_has_no_overlaps(
        game_fs_root, hash_to_path, local_app_id, local_edgemodel_path_hash):
    """Verifies build_blender_materials() gives every dynamically created
    node an explicit position: node_tree.nodes.new(...) never sets
    .location on its own, so without an explicit layout step every
    texture/normal-map node an import creates would land on top of the
    others (and on top of the BSDF), producing an unreadable pile in the
    Shader Editor. Imports real materials from a real .edgemodel and
    asserts the resulting node graph is actually laid out:
    no two nodes visually overlap, and every input node sits left of the
    BSDF it feeds (source-to-sink, left-to-right, matching Blender's own
    node-editor convention and the BSDF/Material Output nodes' own
    positions).
    """
    import bpy

    from albam.engines.hexn.material import build_blender_materials
    from albam.engines.hexn.structs.hexane_edgemodel import HexaneEdgemodel

    path = hash_to_path[local_edgemodel_path_hash]
    edgemodel_bytes = game_fs_root.readbytes(path)
    edgemodel = HexaneEdgemodel.from_bytes(edgemodel_bytes)
    edgemodel._read()

    bl_materials = build_blender_materials(edgemodel, bpy.context)
    assert bl_materials, "expected at least one material to be built"

    materials_with_textures = 0
    for material_path, bl_material in bl_materials.items():
        node_tree = bl_material.node_tree
        bsdf = next(n for n in node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        dynamic_nodes = [n for n in node_tree.nodes if n.type in ("TEX_IMAGE", "NORMAL_MAP")]
        if not dynamic_nodes:
            continue
        materials_with_textures += 1

        for node in dynamic_nodes:
            # Every dynamically created node must have an explicit position -
            # (0, 0) is Blender's un-positioned default, so landing there
            # means the layout step didn't run.
            assert tuple(node.location) != (0.0, 0.0), (
                f"{material_path!r}: {node.name!r} was never positioned"
            )
            assert node.location.x < bsdf.location.x, (
                f"{material_path!r}: {node.name!r} (x={node.location.x}) should be left of "
                f"the BSDF (x={bsdf.location.x}) it feeds into"
            )

        all_nodes = list(node_tree.nodes)
        for i in range(len(all_nodes)):
            for j in range(i + 1, len(all_nodes)):
                a, b = all_nodes[i], all_nodes[j]
                assert not _overlaps(_bbox(a), _bbox(b)), (
                    f"{material_path!r}: {a.name!r} and {b.name!r} overlap "
                    f"({tuple(a.location)} vs {tuple(b.location)})"
                )

    assert materials_with_textures, "expected at least one material with textures to check"
