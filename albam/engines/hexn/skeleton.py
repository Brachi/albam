"""RE:ORC skeleton import (dlc/pack1/Characters/skel/*.ssg) - see
structs/skel.ksy for the file format itself. Builds a real
bpy.types.Armature from the decoded hierarchy + local bind-pose transforms,
mirroring albam.engines.mtfw.mesh.build_blender_armature's Blender-API
shape (a fixed small tail offset per bone rather than connecting to
children - bone rotation isn't needed for a rest pose's head/tail, only
world position).
"""
from pathlib import PureWindowsPath

import bpy
from mathutils import Matrix, Quaternion, Vector

from .structs.hexane_skel import HexaneSkel

# Fixed per-bone tail offset, in Blender units (meters) - human/creature
# skeletons decode to roughly meter-scale bind poses (real samples compose
# to rigs on the order of 1.5-2.5 units tall), so this stays visually
# reasonable without needing per-bone child-distance math.
TAIL_LENGTH = 0.03


def _find_skel_vfile(vfs, stem):
    """A skel file is addressable in the VFS under two different paths,
    depending on how it got mounted, and both need trying:

    - dlc/pack1/Characters/skel/<stem>.ssg (capitalized "Characters", with
      the .ssg extension) - the file's own real on-disk path, exposed when
      whatever was added covers that whole directory (e.g. "Add Folder" on
      the game root, or a parent of it): HexnFS's own loose-file layer
      mirrors real paths directly, case and extension intact.
    - dlc/pack1/characters/skel/<stem> (lowercase "characters", no
      extension) - what the *same* file decodes to when it's added on its
      own (e.g. "Add Files" picking just that one .ssg): a skel/*.ssg is
      itself a single-payload container sharing anims.ksy's big-endian
      shape (see structs/skel.ksy's own doc), and SsgFS/HexnFS expose an
      archive's entries under the name recorded in its own file table, not
      its real on-disk path - confirmed empirically to be this lowercase,
      extension-less form for a skel file's own single entry.

    Both forms point at the identical real bytes; only their VFS
    reachability differs depending on what was added.
    """
    for skel_path in (
        f"dlc/pack1/Characters/skel/{stem}.ssg",
        f"dlc/pack1/characters/skel/{stem}",
    ):
        try:
            return vfs.get_vfile("reorc", skel_path)
        except KeyError:
            continue
    return None


def infer_skeleton_vfile(context, edgemodel_vfile):
    """RE:ORC's skeleton lives in a directory tree entirely separate from
    the mesh that references it: dlc/pack1/Characters/skel/<stem>.ssg (note
    the capitalized "Characters", unlike the lowercase "characters" tree
    the .edgemodel itself is filed under - both confirmed against real
    files). The stem matches the .edgemodel's own filename, not its
    containing directory - a character's .edgemodel can live several
    directories deeper under its own subfolder while its skeleton stays
    directly under skel/<stem>.ssg - confirmed for every real
    playable-character archive directly under dlc/pack1/Characters in a
    full sweep (the small number of *.ssg there without a same-stem
    skel/*.ssg are all non-character utility archives). See
    _find_skel_vfile() for why the stem alone isn't enough to build one
    single lookup path.
    """
    vfs = context.scene.albam.vfs
    stem = PureWindowsPath(edgemodel_vfile.relative_path).stem
    return _find_skel_vfile(vfs, stem)


def build_blender_skeleton(edgemodel_vfile, context, armature_name):
    """Returns (armature_ob, bone_names) for the .edgemodel's matching skel
    file, or (None, None) when there isn't one (e.g. a weapon/prop
    .edgemodel with no skeleton at all) - tolerate-absence convention
    mirrors albam.engines.mtfw.material._infer_mrl() and
    albam.engines.reng.material._get_heuristic_mdf_names().
    """
    skel_vfile = infer_skeleton_vfile(context, edgemodel_vfile)
    if skel_vfile is None:
        return None, None

    return _build_blender_skeleton_from_vfile(skel_vfile, armature_name)


def build_blender_skeleton_by_stem(context, stem, armature_name):
    """Same as build_blender_skeleton(), but for a caller that already
    knows the skeleton's own stem directly - e.g.
    albam.engines.hexn.animation, which gets it straight from a clip's own
    "<clip_path>--<skeleton_name>" name, with no .edgemodel vfile at hand
    to derive it from the way infer_skeleton_vfile() does. Returns
    (None, None) the same way when _find_skel_vfile() can't find the
    skeleton under either of its two addressable paths.
    """
    vfs = context.scene.albam.vfs
    skel_vfile = _find_skel_vfile(vfs, stem)
    if skel_vfile is None:
        return None, None

    return _build_blender_skeleton_from_vfile(skel_vfile, armature_name)


def _build_blender_skeleton_from_vfile(skel_vfile, armature_name):
    skel_bytes = skel_vfile.get_bytes()
    skel = HexaneSkel.from_bytes(skel_bytes)
    skel._read()

    return _build_blender_armature(skel, armature_name)


def _local_matrix(transform):
    rotation = transform.rotation
    position = transform.position
    scale = transform.scale
    # mathutils.Quaternion is (w, x, y, z); skel.ksy's vec4f is (x, y, z, w).
    quat = Quaternion((rotation.w, rotation.x, rotation.y, rotation.z))
    mat_rot = quat.to_matrix().to_4x4()
    mat_trans = Matrix.Translation((position.x, position.y, position.z))
    mat_scale = Matrix.Diagonal((scale.x, scale.y, scale.z, 1.0))
    return mat_trans @ mat_rot @ mat_scale


def _build_blender_armature(skel, armature_name):
    armature = bpy.data.armatures.new(armature_name)
    armature_ob = bpy.data.objects.new(armature_name, armature)
    armature_ob.show_in_front = True

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for ob in bpy.context.scene.objects:
        ob.select_set(False)
    bpy.context.collection.objects.link(armature_ob)
    bpy.context.view_layer.objects.active = armature_ob
    armature_ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")

    world_matrices = []
    edit_bones = []
    bone_names = []
    # Every real skel file in the verified dataset has every parent_index <
    # its own node index (see skel.ksy's hierarchy_entry.parent_index doc) -
    # safe to resolve world transforms and assign parent bones in one
    # forward pass.
    for i, node in enumerate(skel.hierarchy):
        local = _local_matrix(skel.local_transforms[i])
        parent_index = node.parent_index
        world = local if parent_index == -1 else world_matrices[parent_index] @ local
        world_matrices.append(world)

        edit_bone = armature.edit_bones.new(skel.names[i])
        if parent_index != -1:
            edit_bone.parent = edit_bones[parent_index]
        head = world.translation
        # game (x, y, z), Y-up -> Blender (x, -z, y): the same axis
        # convention albam.engines.hexn.mesh already applies to vertex
        # positions, so the armature lines up with the mesh it deforms.
        bl_head = Vector((head.x, -head.z, head.y))
        edit_bone.head = bl_head
        edit_bone.tail = bl_head + Vector((0.0, 0.0, TAIL_LENGTH))
        edit_bones.append(edit_bone)
        bone_names.append(edit_bone.name)  # Blender may have deduped a repeated name

    bpy.ops.object.mode_set(mode="OBJECT")
    return armature_ob, bone_names
