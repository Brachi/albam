"""What a dataset entry records about its .mod, so tests that only apply to
some models can be chosen at collection time (see tests/dataset_cases.py)
instead of skipping at runtime on every model they don't apply to.

Each test file checks the recorded facts against the parsed file, so an
entry can't claim something its model doesn't have.
"""


def mod_facts(mod):
    bones = mod.bones_data.bones_hierarchy if mod.bones_data is not None else []
    return {
        "mod_version": mod.header.version,
        "has_armature": mod.bones_data is not None,
        "has_vertex_colors": any(
            hasattr(v, "rgba") for mesh in mod.meshes_data.meshes for v in mesh.vertices),
        # a bone whose mirror is another bone, as test_guess_mirrors reproduces
        "has_mirrors": any(
            b.idx_mirror < len(bones) and b.idx_mirror != i for i, b in enumerate(bones)),
    }
