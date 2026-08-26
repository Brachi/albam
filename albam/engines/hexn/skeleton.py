"""RE:ORC skeleton import (dlc/pack1/Characters/skel/*.ssg) - see
structs/skel.ksy for the file format itself. Builds a real
bpy.types.Armature from the decoded hierarchy + local bind-pose transforms,
mirroring albam.engines.mtfw.mesh.build_blender_armature's Blender-API
shape, except that each bone's tail points at its own child where the
skeleton gives an unambiguous one (see _bone_tail) so the rig reads as a
skeleton in the viewport instead of a cloud of identical stubs.
"""
from pathlib import PureWindowsPath

import bpy
from mathutils import Matrix, Quaternion, Vector

from .structs.hexane_skel import HexaneSkel

# Fallback tail length, in Blender units (meters), for a bone with no
# single child to point at - human/creature skeletons decode to roughly
# meter-scale bind poses (real samples compose to rigs on the order of
# 1.5-2.5 units tall), so this stays visually reasonable.
TAIL_LENGTH = 0.03

# Blender silently discards a zero-length bone, and these skeletons are full
# of helper nodes sitting a fraction of a millimetre from their parent (the
# "mk_auto" duplicates, among others), so a child this close is not a usable
# tail target and never shortens the bone below this.
MIN_BONE_LENGTH = 0.005

# skel.ksy's `parents` marks a root node with this instead of a real index.
ROOT_PARENT = 0xffff


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


def armature_name_for(stem):
    """The armature name a skeleton gets, from its own stem.

    Both entry points below go through this, and so does
    albam.engines.hexn.animation when it looks for an armature already in
    the scene: a mesh import and a clip import of the same character have
    to land on the same name, or importing a clip after its model builds a
    second armature and animates that one instead.
    """
    return f"{stem}_skeleton"


def build_blender_skeleton(edgemodel_vfile, context):
    """Returns (armature_ob, bone_names) for the .edgemodel's matching skel
    file, or (None, None) when there isn't one (e.g. a weapon/prop
    .edgemodel with no skeleton at all) - tolerate-absence convention
    mirrors albam.engines.mtfw.material._infer_mrl() and
    albam.engines.reng.material._get_heuristic_mdf_names().
    """
    stem = PureWindowsPath(edgemodel_vfile.relative_path).stem
    return build_blender_skeleton_by_stem(context, stem)


def build_blender_skeleton_by_stem(context, stem):
    """Same as build_blender_skeleton(), for a caller that already knows
    the skeleton's own stem - e.g. albam.engines.hexn.animation, which
    gets it straight from a clip's own "<clip_path>--<skeleton_name>"
    name, with no .edgemodel vfile to derive it from. Returns (None, None)
    the same way when _find_skel_vfile() can't find the skeleton under
    either of its two addressable paths.
    """
    vfs = context.scene.albam.vfs
    skel_vfile = _find_skel_vfile(vfs, stem)
    if skel_vfile is None:
        return None, None

    return _build_blender_skeleton_from_vfile(skel_vfile, armature_name_for(stem))


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
    parent_indices = []
    heads = []
    bone_names = []
    # Every real skel file in the verified dataset has every parent index <
    # its own node index (see skel.ksy's `parents` doc) - safe to resolve
    # world transforms and assign parent bones in one forward pass.
    for i, parent_raw in enumerate(skel.parents):
        local = _local_matrix(skel.local_transforms[i])
        parent_index = -1 if parent_raw == ROOT_PARENT else parent_raw
        world = local if parent_index == -1 else world_matrices[parent_index] @ local
        world_matrices.append(world)
        parent_indices.append(parent_index)

        edit_bone = armature.edit_bones.new(skel.names[i])
        if parent_index != -1:
            edit_bone.parent = edit_bones[parent_index]
        head = world.translation
        # game (x, y, z), Y-up -> Blender (x, -z, y): the same axis
        # convention albam.engines.hexn.mesh already applies to vertex
        # positions, so the armature lines up with the mesh it deforms.
        bl_head = Vector((head.x, -head.z, head.y))
        edit_bone.head = bl_head
        heads.append(bl_head)
        edit_bones.append(edit_bone)
        bone_names.append(edit_bone.name)  # Blender may have deduped a repeated name

    # Tails in a second pass: a bone's own children have to exist before it
    # can point at one.
    children = [[] for _ in edit_bones]
    for i, parent_index in enumerate(parent_indices):
        if parent_index != -1:
            children[parent_index].append(i)
    for i, edit_bone in enumerate(edit_bones):
        parent_head = heads[parent_indices[i]] if parent_indices[i] != -1 else None
        edit_bone.tail = _bone_tail(heads[i], parent_head, [heads[c] for c in children[i]])

    bpy.ops.object.mode_set(mode="OBJECT")
    return armature_ob, bone_names


def _bone_tail(head, parent_head, child_heads):
    """Where to put a bone's tail, given its own head, its parent's (None
    for a root) and its children's.

    A skel file stores a position and rotation per node but no bone length
    or direction, so the direction has to come from the rig's own shape.
    A bone with one usable child points straight at it, which is what makes
    a limb read as a limb. At a branch point - and these rigs branch
    constantly, every real joint carrying helper nodes alongside the joint
    that continues the limb - it points at whichever child reaches furthest
    along the direction the bone itself came from, so an elbow follows the
    forearm rather than a helper hanging off the side. A leaf, or a bone
    whose children all sit on top of it or double back, gets a short stub
    continuing that same direction instead.
    """
    targets = [c for c in child_heads if (c - head).length >= MIN_BONE_LENGTH]
    if len(targets) == 1:
        return targets[0]

    direction = head - parent_head if parent_head is not None else None
    if direction is None or direction.length < MIN_BONE_LENGTH:
        direction = Vector((0.0, 0.0, 1.0))
    direction = direction.normalized()

    if targets:
        furthest = max(targets, key=lambda c: (c - head).dot(direction))
        if (furthest - head).dot(direction) >= MIN_BONE_LENGTH:
            return furthest
    return head + direction * TAIL_LENGTH
