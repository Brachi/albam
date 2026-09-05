"""Per-bone data albam keeps for an MT Framework skeleton.

Only the animation id so far: .mod's `idx_anim_map`, the engine-wide bone id
space .lmt tracks are keyed on. It is what lets an .lmt authored for one
character play on another, since import and export address bones through it
rather than through the .mod's own bone order.
"""

import bpy
from mathutils import Vector

from ...registry import blender_registry


# idx_anim_map is a u1 in mod 153, 156 and 21x alike, so one group covers all
MTFW_APP_IDS = ("re0", "re1", "re5", "re6", "rev1", "rev2", "dd", "dmc4", "umvc3")

# Where the re-target id lived before it became an albam custom property. It
# shipped in 0.5.0, so files saved with it are still out there and a read falls
# back and moves it over. The chain properties never shipped, so they need none.
LEGACY_ANIM_RETARGET_PROP = "mtfw.anim_retarget"


@blender_registry.register_custom_properties_bone("mod_bone", MTFW_APP_IDS)
@blender_registry.register_blender_prop
class ModBoneCustomProperties(bpy.types.PropertyGroup):
    # A string, not the u1 it is in the file: a second track on the same id
    # gets a bone of its own, retargeted "<id>_<n>". Empty means unmapped.

    # The bone's left/right counterpart, by name. The format stores an index,
    # but a name survives the bones being reordered or added to, which an index
    # does not. Empty means the bone is its own mirror, which is how the format
    # spells "on the midline" - 38% of bones in a real skeleton.
    #
    # Held rather than computed because it cannot be computed: pairing each bone
    # with the one whose rest position is its X-mirror gets 70.8% of them right
    # over a large sample, losing on bones that share a rest position, where
    # nothing geometric tells the candidates apart.
    mirror: bpy.props.StringProperty(
        name="Mirror Bone",
        description="Name of this bone's left/right counterpart. Empty means the bone "
                    "is its own mirror",
        default="",
        options=set(),
    )

    anim_retarget: bpy.props.StringProperty(
        name="Anim Retarget",
        description="Animation bone id this bone answers to, from the .mod's idx_anim_map",
        default="",
        options=set(),
    )
    # A limb is not keyed as a finished pose: the goal it is solved towards
    # rides its own control bone, which is what these mark. Import leaves that
    # bone's position channel unconverted, and export has to do the same.
    chain_target: bpy.props.BoolProperty(
        name="Chain Target",
        description="This bone carries a limb chain's goal rather than a joint's own transform",
        default=False,
        options=set(),
    )
    chain_length: bpy.props.IntProperty(
        name="Chain Length",
        description="Joints the solver owns, plus the target",
        default=0,
        options=set(),
    )


def get_bone_custom_properties(pose_bone, app_id):
    """Takes a pose bone (`armature_obj.pose.bones[...]`), where the group lives."""
    return pose_bone.albam_custom_properties.get_custom_properties_for_appid(app_id)


def get_anim_retarget(pose_bone, app_id):
    props = get_bone_custom_properties(pose_bone, app_id)
    if not props.anim_retarget:
        legacy = pose_bone.bone.get(LEGACY_ANIM_RETARGET_PROP)
        if legacy is not None:
            props.anim_retarget = str(legacy)
    return props.anim_retarget


def set_anim_retarget(pose_bone, app_id, value):
    get_bone_custom_properties(pose_bone, app_id).anim_retarget = value


def get_chain_target(pose_bone, app_id):
    return get_bone_custom_properties(pose_bone, app_id).chain_target


def get_chain_length(pose_bone, app_id):
    return get_bone_custom_properties(pose_bone, app_id).chain_length


def set_chain_target(pose_bone, app_id, chain_length):
    props = get_bone_custom_properties(pose_bone, app_id)
    props.chain_target = True
    props.chain_length = chain_length


def get_mirror(pose_bone, app_id):
    return get_bone_custom_properties(pose_bone, app_id).mirror


def set_mirror(pose_bone, app_id, value):
    get_bone_custom_properties(pose_bone, app_id).mirror = value


# How close two joints must sit to count as occupying the same point. Positions
# are emitted by whatever authored the model rather than measured, so the
# reflection is exact and this only has to absorb float noise: 1e-5 metres, or
# a thousandth of a unit at the scale the file stores.
SYMMETRY_TOLERANCE = 1e-5


def _same_point(a, b):
    return (a - b).length <= SYMMETRY_TOLERANCE


def _subtree_sizes(parent_of, count):
    """(direct children, all descendants) per bone."""
    children = [[] for _ in range(count)]
    for i, parent in enumerate(parent_of):
        if parent is not None:
            children[parent].append(i)
    descendants = [0] * count
    for i in reversed(range(count)):
        descendants[i] = len(children[i]) + sum(descendants[c] for c in children[i])
    return [len(c) for c in children], descendants


def guess_mirrors(armature_ob):
    """Work out each bone's mirror from the rest pose, as {bone name: name}.

    Two facts drive this, and both hold without exception across a large sample
    of real models:

    * A joint on the midline mirrors itself, and one off it never does. Every
      self-mirroring bone measured sits at x = 0, every paired bone does not,
      and no bone lacking a mirror sits on the midline. So which of the three
      states a bone is in is decided by its x alone.
    * A paired joint's partner sits at its own position reflected across x,
      exactly. The partner is at that point for every pair measured, so
      reflection never misses - whatever authored these computed them this way.

    What reflection cannot do is *order* candidates when several joints occupy
    one point, which is common. Those are settled by preferring a candidate
    hanging off the mirror of the bone's own parent, then one whose subtree is
    the same shape, then one the same distance from its parent.

    Measured against real models this reproduces every bone of four models in
    five, and about 98% of bones overall. Where it fails it is not close: the
    remainder are joints stacked several deep on one point, identical in parent,
    children and distance, which nothing short of the original author's intent
    separates. One creature rig alone, with two thirds of its joints sharing a
    position with three others, accounts for a large share of them.

    So this seeds a value for a human to check rather than something to write
    unattended, and export keeps reading what the rig actually says.
    """
    bl_bones = list(armature_ob.data.bones)
    positions = [bl_bone.head_local for bl_bone in bl_bones]
    index_of = {bl_bone.name: i for i, bl_bone in enumerate(bl_bones)}
    parent_of = [index_of.get(b.parent.name) if b.parent else None for b in bl_bones]
    num_children, num_descendants = _subtree_sizes(parent_of, len(bl_bones))

    mirror = [None] * len(bl_bones)
    candidates = [[] for _ in bl_bones]
    undecided = []
    for i, position in enumerate(positions):
        if abs(position.x) <= SYMMETRY_TOLERANCE:
            mirror[i] = i
            continue
        target = Vector((-position.x, position.y, position.z))
        found = [j for j in range(len(bl_bones))
                 if j != i and _same_point(positions[j], target)]
        candidates[i] = found
        if len(found) == 1:
            mirror[i] = found[0]
        elif found:
            undecided.append(i)

    # Fewest candidates first, so the easier joints are settled before they are
    # needed to narrow the harder ones.
    for i in sorted(undecided, key=lambda i: len(candidates[i])):
        parent_mirror = mirror[parent_of[i]] if parent_of[i] is not None else None
        pool = [j for j in candidates[i] if parent_of[j] == parent_mirror] or candidates[i]
        unclaimed = [j for j in pool if mirror[j] is None or mirror[j] == i]
        pool = unclaimed or pool

        def distance_to_parent(j):
            parent = parent_of[j]
            return (positions[j] - positions[parent]).length if parent is not None else 0.0

        own_distance = distance_to_parent(i)

        def resemblance(j):
            return (abs(num_children[j] - num_children[i]),
                    abs(num_descendants[j] - num_descendants[i]),
                    abs(distance_to_parent(j) - own_distance))

        mirror[i] = min(pool, key=resemblance)

    return {bl_bones[i].name: bl_bones[j].name
            for i, j in enumerate(mirror) if j is not None}
