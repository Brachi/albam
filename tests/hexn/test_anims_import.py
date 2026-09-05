"""
Blender import correctness test for RE:ORC animation clips (see
albam.engines.hexn.animation.import_anim_clip and structs/anims.ksy).

Drives a real bpy.ops.albam.import_vfile() import through the actual
registry/VFS/UI operator stack (mirrors test_skeleton_import.py's own
shape) - mounts the whole game root (so both the .anims.ssg's own clip
listing, via fs.py's dual-format SsgFS, and the referenced skeleton's
dlc/pack1/Characters/skel/*.ssg are reachable), selects one specific real
clip inside a real *.anims.ssg archive, and asserts a real Action with
real keyframed fcurves ends up applied to a real, correctly-named
Armature.

Reuses one of test_anims_parsing.py's own committed hashes rather than
adding a new one - which specific clip to import is picked dynamically by
decoding the archive and choosing one with real animated
rotation/translation channels (mirrors test_edgemodel_parsing.py's own
test_non_52_stride_produces_a_coherent_mesh, which similarly picks a
specific sub-entry out of an already hash-verified file rather than
needing its own separate hash).
"""
import bpy


ANIMS_HASH = "0aadc76ea27d6c42"


def pytest_generate_tests(metafunc):
    if "local_app_id" in metafunc.fixturenames:
        metafunc.parametrize("local_app_id", ["reorc"], scope="session")


def _pick_animated_clip(anims):
    """A clip with at least one real animated rotation and translation
    channel (not just constant/no-op ones) - see animation.py's own
    module doc for why that matters (the interesting code path)."""
    offset = 0
    for file_info in anims.files_info:
        clip_bytes = anims.buffer_chunks[offset:offset + file_info.size]
        offset += file_info.size
        clip = type(anims).AnimClip.from_bytes(clip_bytes)
        clip._read()
        if clip.num_anim_r_channels > 0 and clip.num_anim_t_channels > 0:
            return file_info
    raise AssertionError("no clip with real animated channels found in this archive")


def test_import_applies_action_to_a_real_armature(game_fs_root, hash_to_path, local_app_id):
    from albam.engines.hexn.structs.hexane_anims import HexaneAnims

    path = hash_to_path[ANIMS_HASH]
    anims_bytes = game_fs_root.readbytes(path)
    anims = HexaneAnims.from_bytes(anims_bytes)
    anims._read()
    file_info = _pick_animated_clip(anims)
    clip_path, skeleton_name = file_info.name.rsplit("--", 1)
    assert skeleton_name and skeleton_name.islower()

    # Mirrors fs.py's SsgFS: the clip's own virtual leaf path inside the
    # whole-game-root-mounted VFS is its real inner name (forward
    # slashes, no leading slash for select_vfile - see
    # test_skeleton_import.py's own .lstrip("/") precedent) plus the
    # synthetic ".animclip" suffix.
    clip_vfile_path = file_info.name.replace("\\", "/").lstrip("/") + ".animclip"

    vfs = bpy.context.scene.albam.vfs
    vfs.select_vfile(local_app_id, clip_vfile_path)
    before = set(bpy.data.objects)

    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}

    # import_anim_clip() returns None (see its own docstring) and applies
    # the action to an already-existing or freshly-built armature - either
    # way, no *new* top-level bpy.data.objects should appear for a clip
    # import once the armature already exists; the first import of a given
    # character does create one, so check for it directly by name instead
    # of diffing `before`.
    from albam.engines.hexn.skeleton import armature_name_for, find_skel_vfile

    skel_vfile = find_skel_vfile(bpy.context, skeleton_name)
    armature_ob = bpy.data.objects.get(armature_name_for(skel_vfile))
    assert armature_ob is not None
    assert armature_ob.type == "ARMATURE"

    assert armature_ob.animation_data is not None
    action = armature_ob.animation_data.action
    assert action is not None

    all_fcurves = []
    for layer in action.layers:
        for strip in layer.strips:
            for channelbag in strip.channelbags:
                all_fcurves.extend(channelbag.fcurves)
    assert all_fcurves, "expected at least one fcurve on the imported action"

    bone_names = {b.name for b in armature_ob.pose.bones}
    location_curves = [fc for fc in all_fcurves if fc.data_path.endswith(".location")]
    rotation_curves = [fc for fc in all_fcurves if fc.data_path.endswith(".rotation_quaternion")]
    assert location_curves and rotation_curves
    for fc in all_fcurves:
        # data_path is pose.bones["<name>"].location / .rotation_quaternion
        bone_name = fc.data_path.split('"')[1]
        assert bone_name in bone_names
        assert len(fc.keyframe_points) > 0

    # A second clip for the *same* skeleton reuses the existing armature
    # rather than building a duplicate (see skeleton.armature_name_for's
    # reuse-by-name convention).
    second_file_info = next(
        fi for fi in anims.files_info
        if fi.name != file_info.name and fi.name.endswith(f"--{skeleton_name}")
    )
    second_clip_path = second_file_info.name.replace("\\", "/").lstrip("/") + ".animclip"
    vfs.select_vfile(local_app_id, second_clip_path)
    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}

    armatures_after = [
        ob for ob in bpy.data.objects if ob.type == "ARMATURE" and ob.name.startswith(skeleton_name)
    ]
    assert len(armatures_after) == 1, f"expected the same armature to be reused, got {armatures_after}"
    assert armature_ob.animation_data.action is not action, (
        "second import should have created its own new Action, not reused the first clip's"
    )

    # Not "the armature is new since `before`": whether this import is the
    # one that creates it depends on whether an earlier test in the session
    # already imported something for this same character. What matters here
    # is that a clip import produces no *extra* objects beyond the armature
    # it needs - asserted by the single-armature check above, plus no stray
    # meshes or empties appearing.
    added = [ob for ob in bpy.data.objects if ob not in before and ob is not armature_ob]
    assert not added, f"a clip import should not create anything besides its armature, got {added}"
