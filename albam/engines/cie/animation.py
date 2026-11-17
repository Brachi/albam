"""Importing a skeletal motion (.fcv) onto an imported RE4UHD armature.

An .fcv names no skeleton: its joints are bone ids (see
structs/re4-uhd-fcv.ksy), which is also what the .bin importer names an
armature's bones after, so a motion goes onto whichever armature the import
panel points at, the same way an MT Framework .lmt does.

The keys cannot be copied onto pose bones one for one. Arms and legs are IK
chains: the file keys the chain's upper bone and, on its end bone (ankle or
wrist), a position in model space that the limb has to reach, plus the end
bone's orientation relative to the model. Knees and elbows are not keyed at
all, and a target read as a bone translation tears the limb off. So every
frame is evaluated here and baked into one key per frame per moved bone:

1. the Hermite curves give each keyed bone its local rotation (Euler XYZ),
   translation or scale, and the root motion places the model;
2. each limb is solved as a two-bone IK (`_Limb`): the upper and lower bones
   keep their rest lengths, the knee or elbow bends in the plane picked by
   the joint's channel seen from the upper bone's keyed orientation, and the
   end bone keeps its keyed orientation relative to the model; on arms the
   wrist's twist about the forearm is spread over the forearm helper bones;
3. the "double joint" helpers listed in the model's .bin take the slerp of
   the two bones they sit between.

This evaluator was written from a behavioural description of the format,
checked against the game's own data (toes landing on their targets, limb
lengths kept, knees bending forward and elbows backward), not from the
game's code. The twist falloff in particular is an approximation. The clip
plays as it does in the game, at the cost of not being an IK rig that can be
re-posed by hand.

Root motion (the character's own displacement over the clip, which the game
applies to the model rather than to a part) is applied to the armature's
root bones, so a walk walks.
"""
from bisect import bisect_right
import math

import bpy
from mathutils import Euler, Matrix, Quaternion, Vector

from ...exceptions import AlbamCheckFailure
from ...lib.blender import get_action_channels
from ...registry import blender_registry
from .mesh import BONE_PAIRS_PROPERTY, GLOBAL_SCALE
from .structs.re4_uhd_fcv import Re4UhdFcv

# Joint kinds (see joint_info.kind in the .ksy).
KIND_ROOT_POSITION = 0x01
KIND_ROOT_ROTATION = 0x40
KIND_ROTATION = 0x02
KIND_TRANSLATION = 0x04
KIND_SCALE = 0x08
KIND_IK_ROOT = 0x30
KIND_IK_TOE = 0x20
KIND_IK_FOUR_JOINTS = 0x80

# On a chain's upper bone, the channel is the direction the middle joint
# (knee, elbow) bends towards, in the upper bone's own posed frame. Every
# leg in the game uses 4 (+z, forward) and every arm 5 (-z, backwards).
IK_POLE_DIRECTIONS = {
    0: Vector((0.0, 1.0, 0.0)),
    1: Vector((0.0, -1.0, 0.0)),
    2: Vector((1.0, 0.0, 0.0)),
    3: Vector((-1.0, 0.0, 0.0)),
    4: Vector((0.0, 0.0, 1.0)),
    5: Vector((0.0, 0.0, -1.0)),
}
CAMERA_CHANNELS = (6, 7)

# A basis this close to identity on every frame is a bone the motion left
# alone, and gets no keys.
STATIC_EPSILON = 1e-5
# Shorter than this (in model units, millimetres) is no bone at all.
MIN_BONE_LENGTH = 1e-3

# Game space (Y up, model units) to an armature's (Z up, metres), the same
# swap and scale the .bin importer builds the bones with (mesh._yz_flip).
GAME_TO_BLENDER = Matrix((
    (GLOBAL_SCALE, 0.0, 0.0, 0.0),
    (0.0, 0.0, -GLOBAL_SCALE, 0.0),
    (0.0, GLOBAL_SCALE, 0.0, 0.0),
    (0.0, 0.0, 0.0, 1.0),
))
BLENDER_TO_GAME = GAME_TO_BLENDER.inverted()


def _hermite(p0, m0, p1, m1, t):
    """The cubic Hermite segment from p0 to p1 at t in [0, 1], with m0 and
    m1 the tangents in units of the whole segment."""
    t2 = t * t
    t3 = t2 * t
    return ((2.0 * t3 - 3.0 * t2 + 1.0) * p0 +
            (t3 - 2.0 * t2 + t) * m0 +
            (3.0 * t2 - 2.0 * t3) * p1 +
            (t3 - t2) * m1)


def _curve_value(axis, frame):
    """One scalar curve at `frame`: held before the first and after the last
    key, Hermite in between.

    The tangents are not multiplied by the key interval. Measured over every
    Leon motion they track the value change across the whole segment (a
    median ratio of 0.87) and not the change per frame (2.9, about the usual
    three frame interval), so they are already in segment units.
    """
    frames = axis.frames
    keys = axis.keys
    if not keys:
        return 0.0
    if frame <= frames[0]:
        return keys[0].value
    if frame >= frames[-1]:
        return keys[-1].value
    i = bisect_right(frames, frame) - 1
    k0, k1 = keys[i], keys[i + 1]
    span = frames[i + 1] - frames[i]
    t = (frame - frames[i]) / span if span else 0.0
    return _hermite(k0.value, k0.out_tangent, k1.value, k1.in_tangent, t)


def _axes_value(joint, frame):
    """A joint's three curves at `frame`, as a vector."""
    return Vector([_curve_value(axis, frame) for axis in joint.axes])


def _euler_quaternion(xyz):
    """Rotation keys are radians applied x, then y, then z."""
    return Euler(xyz, 'XYZ').to_quaternion()


def _rotation_of(matrix):
    return matrix.to_quaternion().normalized()


def _twist_angle(rotation, axis):
    """The signed angle of `rotation`'s twist about the unit `axis`
    (swing-twist decomposition), in [-pi, pi]."""
    along = rotation.x * axis.x + rotation.y * axis.y + rotation.z * axis.z
    angle = 2.0 * math.atan2(along, rotation.w)
    if angle > math.pi:
        angle -= 2.0 * math.pi
    elif angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


class _Limb:
    """One IK chain of a motion on one skeleton.

    `upper` is the joint's bone (thigh, upper arm), `lower` the next one
    (shin, forearm), `helpers` the forearm twist bones between `lower` and
    `end` (only with KIND_IK_FOUR_JOINTS), `end` the ankle or wrist, and
    `toe` the end's child whose head the target places, on legs.
    """

    def __init__(self, joint, skeleton):
        kind = joint.info.kind
        self.upper = joint.parts_no
        self.channel = joint.info.channel
        four = bool(kind & KIND_IK_FOUR_JOINTS)
        self.lower = self.upper + 1
        self.helpers = [self.upper + 2] if four else []
        self.end = self.upper + (3 if four else 2)
        self.toe = self.end + 1 if (kind & KIND_IK_TOE and not four) else None
        self.problem = self._check(skeleton)

    @property
    def label(self):
        return f"{self.upper}-{self.end}"

    def bones(self):
        return [self.upper, self.lower, *self.helpers, self.end]

    def _check(self, skeleton):
        """Why this chain cannot be solved on `skeleton`, or None."""
        if self.channel not in IK_POLE_DIRECTIONS:
            return f"channel {self.channel} is not a bend direction"
        ids = self.bones() + ([self.toe] if self.toe is not None else [])
        missing = [i for i in ids if i not in skeleton.names]
        if missing:
            return f"no bone {', '.join(map(str, missing))}"
        for child, parent in zip(ids[1:], ids[:-1]):
            if skeleton.parent[child] != parent:
                return f"bone {child} is not a child of {parent}"
        self.upper_length = skeleton.rest_local[self.lower].length
        self.lower_offset = sum((skeleton.rest_local[i] for i in self.helpers + [self.end]), Vector())
        self.lower_length = self.lower_offset.length
        if self.upper_length < MIN_BONE_LENGTH or self.lower_length < MIN_BONE_LENGTH:
            return "a bone of it has no length at rest"
        # How far along the forearm each helper sits, for the twist falloff.
        self.helper_fractions = []
        walked = Vector()
        for helper in self.helpers:
            walked = walked + skeleton.rest_local[helper]
            along = walked.dot(self.lower_offset) / (self.lower_length ** 2)
            self.helper_fractions.append(min(1.0, max(0.0, along)))
        return None

    def solve(self, pose, target, end_rotation):
        """Pose this limb so its end (or toe) reaches `target`, the end
        bone turned to `end_rotation`; both in world space."""
        skeleton = pose.skeleton
        upper_world = pose.world[self.upper]
        root = upper_world.translation
        upper_rotation = _rotation_of(upper_world)

        reach = target
        if self.toe is not None:
            reach = target - end_rotation @ skeleton.rest_local[self.toe]

        a, b = self.upper_length, self.lower_length
        to_reach = reach - root
        distance = to_reach.length
        if distance > 1e-9:
            direction = to_reach / distance
        else:
            direction = (upper_rotation @ skeleton.rest_local[self.lower]).normalized()
        distance = min(max(distance, abs(a - b)), a + b)

        pole = upper_rotation @ IK_POLE_DIRECTIONS[self.channel]
        side = pole - direction * pole.dot(direction)
        if side.length < 1e-9:
            side = direction.orthogonal()
        side.normalize()

        # Law of cosines: how far along `direction` the middle joint sits,
        # and how far out to the side.
        along = (a * a - b * b + distance * distance) / (2.0 * distance) if distance > 1e-9 else 0.0
        out = math.sqrt(max(0.0, a * a - along * along))
        middle = root + direction * along + side * out
        end = root + direction * distance

        upper_bone = upper_rotation @ skeleton.rest_local[self.lower]
        new_upper = upper_bone.rotation_difference(middle - root) @ upper_rotation
        lower_fk = new_upper @ pose.local_rotation[self.lower]
        lower_bone = lower_fk @ self.lower_offset
        new_lower = lower_bone.rotation_difference(end - middle) @ lower_fk

        parent_rotation = pose.parent_world_rotation(self.upper)
        pose.local_rotation[self.upper] = parent_rotation.inverted() @ new_upper
        pose.local_rotation[self.lower] = new_upper.inverted() @ new_lower

        # Spread the wrist's twist about the forearm over the helpers,
        # each turned by the fraction of the forearm it sits along. A
        # linear falloff is an approximation of what the game does.
        previous = new_lower
        if self.helpers:
            axis = self.lower_offset.normalized()
            twist = _twist_angle(new_lower.inverted() @ end_rotation, axis)
            for helper, fraction in zip(self.helpers, self.helper_fractions):
                helper_world = new_lower @ Quaternion(axis, twist * fraction)
                pose.local_rotation[helper] = previous.inverted() @ helper_world
                previous = helper_world
        pose.local_rotation[self.end] = previous.inverted() @ end_rotation
        pose.local_position[self.end] = skeleton.rest_local[self.end].copy()
        pose.update(self.upper)


class _Pose:
    """One frame's local transforms per bone and the world matrices they
    make. A world matrix maps a bone's own space (rest head at the origin,
    model axes) to the world, the model's root motion included."""

    def __init__(self, skeleton, children):
        self.skeleton = skeleton
        self.children = children
        self.model = Matrix.Identity(4)
        self.local_position = {}
        self.local_rotation = {}
        self.local_scale = {}
        self.world = {}

    def reset(self, model):
        self.model = model
        for bone_id in self.skeleton.order:
            self.local_position[bone_id] = self.skeleton.rest_local[bone_id].copy()
            self.local_rotation[bone_id] = Quaternion()
            self.local_scale[bone_id] = Vector((1.0, 1.0, 1.0))

    def parent_world(self, bone_id):
        parent_id = self.skeleton.parent[bone_id]
        return self.world[parent_id] if parent_id is not None else self.model

    def parent_world_rotation(self, bone_id):
        return _rotation_of(self.parent_world(bone_id))

    def _local_matrix(self, bone_id):
        return Matrix.LocRotScale(
            self.local_position[bone_id], self.local_rotation[bone_id], self.local_scale[bone_id])

    def update(self, bone_id=None):
        """Recompute the world matrices of `bone_id` and everything under
        it, or of the whole skeleton."""
        if bone_id is None:
            for b in self.skeleton.order:
                self.world[b] = self.parent_world(b) @ self._local_matrix(b)
            return
        stack = [bone_id]
        while stack:
            b = stack.pop()
            self.world[b] = self.parent_world(b) @ self._local_matrix(b)
            stack.extend(self.children.get(b, ()))


def _usable_joints(fcv):
    """(joints, skipped): the joints whose keys read and that drive a
    skeleton, and a description of each one left out. A handful of weapon
    motions carry broken camera joints the game never reads; one of those
    should not cost the rest of the motion."""
    joints, skipped = [], []
    for i, joint in enumerate(fcv.joints):
        try:
            channel = joint.info.channel
            if channel in CAMERA_CHANNELS:
                skipped.append(f"joint {i} (camera channel {channel})")
                continue
            for axis in joint.axes:
                axis.keys
        except Exception as error:
            skipped.append(f"joint {i} ({error})")
            continue
        joints.append(joint)
    return joints, skipped


class _Motion:
    """A motion's joints sorted by what they drive, against one skeleton."""

    def __init__(self, joints, skeleton):
        self.root_position = None
        self.root_rotation = None
        self.rotation = {}
        self.translation = {}
        self.scale = {}
        self.limbs = []
        self.skipped_limbs = []
        for joint in joints:
            kind = joint.info.kind
            bone_id = joint.parts_no
            if kind == KIND_ROOT_POSITION:
                self.root_position = joint
            elif kind == KIND_ROOT_ROTATION:
                self.root_rotation = joint
            elif kind & KIND_ROTATION:
                self.rotation[bone_id] = joint
            elif kind & KIND_TRANSLATION:
                self.translation[bone_id] = joint
            elif kind & KIND_SCALE:
                self.scale[bone_id] = joint
            elif kind & KIND_IK_ROOT:
                # The chain's own curves are its upper bone's rotation.
                self.rotation[bone_id] = joint
                limb = _Limb(joint, skeleton)
                if limb.problem is None:
                    self.limbs.append(limb)
                else:
                    self.skipped_limbs.append(limb)
        # The end bone of every chain is keyed in model space, solved or not;
        # only a solved chain may use its translation keys, as a target.
        self.model_space_ends = {limb.end for limb in self.limbs + self.skipped_limbs}
        self.targets = {limb.end for limb in self.limbs}

    def model_matrix(self, frame):
        model = Matrix.Identity(4)
        if self.root_position is not None:
            model = Matrix.Translation(_axes_value(self.root_position, frame))
        if self.root_rotation is not None:
            model = model @ _euler_quaternion(_axes_value(self.root_rotation, frame)).to_matrix().to_4x4()
        return model


def evaluate_motion(joints, skeleton, double_joints, num_frames):
    """{bone id: [world matrix per frame]} for every bone of `skeleton`, and
    the chains that could not be solved on it (see _Limb.problem).

    `joints` are the motion's usable joints (_usable_joints) and
    `double_joints` the (helper, bone a, bone b, fraction) lines that apply
    to the skeleton (_double_joints).
    """
    motion = _Motion(joints, skeleton)
    children = {}
    for bone_id in skeleton.order:
        parent_id = skeleton.parent[bone_id]
        if parent_id is not None:
            children.setdefault(parent_id, []).append(bone_id)
    pose = _Pose(skeleton, children)
    worlds = {bone_id: [] for bone_id in skeleton.order}
    known = skeleton.names

    for frame in range(num_frames):
        model = motion.model_matrix(frame)
        pose.reset(model)
        model_rotation = _rotation_of(model)
        end_rotations = {}
        for bone_id, joint in motion.rotation.items():
            if bone_id not in known:
                continue
            rotation = _euler_quaternion(_axes_value(joint, frame))
            if bone_id in motion.model_space_ends:
                end_rotations[bone_id] = model_rotation @ rotation
            else:
                pose.local_rotation[bone_id] = rotation
        for bone_id, joint in motion.translation.items():
            if bone_id in known and bone_id not in motion.model_space_ends:
                pose.local_position[bone_id] = _axes_value(joint, frame)
        for bone_id, joint in motion.scale.items():
            if bone_id in known:
                pose.local_scale[bone_id] = _axes_value(joint, frame)
        pose.update()

        # An unsolved chain's end still turns the way the model says.
        for limb in motion.skipped_limbs:
            if limb.end in end_rotations:
                parent_rotation = pose.parent_world_rotation(limb.end)
                pose.local_rotation[limb.end] = parent_rotation.inverted() @ end_rotations[limb.end]
                pose.update(limb.end)

        for limb in motion.limbs:
            end_rotation = end_rotations.get(limb.end)
            if end_rotation is None:
                end_rotation = _rotation_of(pose.world[limb.end])
            target_joint = motion.translation.get(limb.end)
            if target_joint is None:
                # Nothing to reach for: keep the limb where it is.
                parent_rotation = pose.parent_world_rotation(limb.end)
                pose.local_rotation[limb.end] = parent_rotation.inverted() @ end_rotation
                pose.update(limb.end)
                continue
            target = model @ _axes_value(target_joint, frame)
            limb.solve(pose, target, end_rotation)

        for helper, bone_a, bone_b, fraction in double_joints:
            blended = _rotation_of(pose.world[bone_a]).slerp(_rotation_of(pose.world[bone_b]), fraction)
            pose.local_rotation[helper] = pose.parent_world_rotation(helper).inverted() @ blended
            pose.update(helper)

        for bone_id in skeleton.order:
            worlds[bone_id].append(pose.world[bone_id].copy())
    return worlds, motion.skipped_limbs


def _double_joints(armature, skeleton):
    """The double joint lines (see mesh.BONE_PAIRS_PROPERTY) of the meshes
    deformed by `armature`, as (helper, bone a, bone b, fraction), first
    seen first, keeping only those whose bones the skeleton has. A helper
    must not be an ancestor of either bone it blends."""
    lines = []
    seen = set()
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        deformed = ob.parent == armature or any(
            m.type == 'ARMATURE' and m.object == armature for m in ob.modifiers)
        raw = ob.get(BONE_PAIRS_PROPERTY) if deformed else None
        if not raw:
            continue
        raw = list(raw)
        for i in range(0, len(raw) - 3, 4):
            line = tuple(int(v) for v in raw[i:i + 4])
            if line in seen:
                continue
            seen.add(line)
            helper, bone_a, bone_b, percent = line
            if not all(b in skeleton.names for b in (helper, bone_a, bone_b)):
                continue
            if _is_ancestor(skeleton, helper, bone_a) or _is_ancestor(skeleton, helper, bone_b):
                continue
            lines.append((helper, bone_a, bone_b, percent / 100.0))
    return lines


def _is_ancestor(skeleton, ancestor, bone_id):
    while bone_id is not None:
        if bone_id == ancestor:
            return True
        bone_id = skeleton.parent[bone_id]
    return False


class _Skeleton:
    """The armature's bones in the game's terms: parent and rest offset per
    bone id, read back off the bones the .bin importer made (whose heads are
    the game's rest positions, swapped and scaled)."""

    def __init__(self, armature):
        self.names = {}
        for bone in armature.data.bones:
            try:
                self.names[int(bone.name)] = bone.name
            except ValueError:
                continue
        # Parents before children, which is also the order the game walks
        # its parts in (they are listed by bone id).
        self.order = sorted(self.names)
        self.parent = {}
        self.rest_world = {}
        self.rest_local = {}
        self.rest_matrix = {}
        for bone_id in self.order:
            bone = armature.data.bones[self.names[bone_id]]
            parent = bone.parent
            parent_id = None
            if parent is not None:
                try:
                    parent_id = int(parent.name)
                except ValueError:
                    parent_id = None
            if parent_id not in self.names:
                parent_id = None
            self.parent[bone_id] = parent_id
            self.rest_world[bone_id] = (BLENDER_TO_GAME @ bone.head_local.to_4d()).to_3d()
            self.rest_matrix[bone_id] = bone.matrix_local.copy()
        for bone_id in self.order:
            parent_id = self.parent[bone_id]
            parent_rest = self.rest_world[parent_id] if parent_id is not None else Vector()
            self.rest_local[bone_id] = self.rest_world[bone_id] - parent_rest


def _pose_bases(skeleton, armature, worlds, num_frames):
    """{bone name: [matrix_basis per frame]} reproducing `worlds`.

    A game world matrix moves a vertex from its rest position to its posed
    one; conjugated into armature space that is the bone's deformation D,
    and a pose bone's basis is that deformation seen from its own rest
    frame and relative to its parent's: R^-1 * Dparent^-1 * D * R.
    """
    deform = {}
    for bone_id, frames in worlds.items():
        unrest = Matrix.Translation(-skeleton.rest_world[bone_id])
        deform[bone_id] = [GAME_TO_BLENDER @ w @ unrest @ BLENDER_TO_GAME for w in frames]
    bases = {}
    for bone_id in skeleton.order:
        name = skeleton.names[bone_id]
        bone = armature.data.bones[name]
        rest = skeleton.rest_matrix[bone_id]
        rest_inv = rest.inverted_safe()
        parent_id = None
        if bone.parent is not None:
            try:
                parent_id = int(bone.parent.name)
            except ValueError:
                parent_id = None
        frames = []
        for f in range(num_frames):
            d = deform[bone_id][f]
            if parent_id in deform:
                d = deform[parent_id][f].inverted_safe() @ d
            frames.append(rest_inv @ d @ rest)
        bases[name] = frames
    return bases


def _is_static(frames):
    identity = Matrix.Identity(4)
    return all(
        abs(m[r][c] - identity[r][c]) < STATIC_EPSILON
        for m in frames for r in range(4) for c in range(4))


def _key_bases(action, armature, bases):
    channels = get_action_channels(action, armature.name)
    for name, frames in bases.items():
        if _is_static(frames):
            continue
        armature.pose.bones[name].rotation_mode = 'QUATERNION'
        group = channels.groups.get(name) or channels.groups.new(name)
        locations, rotations, scales = [], [], []
        previous = None
        for m in frames:
            loc, rot, sca = m.decompose()
            # Keep neighbouring quaternions on the same side, or the
            # interpolation between keys takes the long way round.
            if previous is not None and previous.dot(rot) < 0:
                rot = Quaternion((-rot.w, -rot.x, -rot.y, -rot.z))
            previous = rot
            locations.append(loc)
            rotations.append(rot)
            scales.append(sca)
        for path, values, size in (("location", locations, 3),
                                   ("rotation_quaternion", rotations, 4),
                                   ("scale", scales, 3)):
            data_path = f'pose.bones["{name}"].{path}'
            for index in range(size):
                curve = channels.fcurves.new(data_path=data_path, index=index)
                curve.group = group
                curve.keyframe_points.add(len(values))
                coords = []
                for frame, value in enumerate(values):
                    coords.extend((frame + 1, value[index]))
                curve.keyframe_points.foreach_set("co", coords)
                for point in curve.keyframe_points:
                    point.interpolation = 'LINEAR'
                curve.update()


def _parse_fcv(fcv_bytes):
    """The motion's header and joint table. The joints' keys are read
    lazily, and one at a time by _usable_joints, so a broken joint costs
    only itself."""
    fcv = Re4UhdFcv.from_bytes(fcv_bytes)
    fcv._read()
    fcv.joints
    return fcv


@blender_registry.register_import_function(app_id="re4uhd", extension="fcv", albam_asset_type="ANIMATION")
def load_fcv(vfile, context):
    armature = context.scene.albam.import_options_fcv.armature
    if armature is None or armature.type != 'ARMATURE':
        raise AlbamCheckFailure(
            "No armature to put the motion on",
            details="An .fcv carries no skeleton, only bone ids.",
            solution="Import the character's model first and pick its armature in the FCV options.",
        )
    try:
        fcv = _parse_fcv(vfile.get_bytes())
    except Exception as error:
        raise AlbamCheckFailure(
            "This .fcv does not read as a motion",
            details=f"{vfile.display_name}: {error}",
            solution="Check that the file is a motion from an RE4UHD character archive.",
        ) from error
    joints, skipped_joints = _usable_joints(fcv)
    if fcv.num_joints and not joints:
        if all("camera channel" in reason for reason in skipped_joints):
            raise AlbamCheckFailure(
                "This .fcv moves a camera, not a skeleton",
                details=f"{vfile.display_name}: every joint is on a camera channel.",
                solution="Camera motions are not supported yet.",
            )
        raise AlbamCheckFailure(
            "None of this .fcv's joints read",
            details=f"{vfile.display_name}: {'; '.join(skipped_joints[:5])}",
            solution="A few weapon motions ship broken, with keys the game never reads; "
                     "those cannot be imported.",
        )
    skeleton = _Skeleton(armature)
    parts = {j.parts_no for j in joints}
    if fcv.num_joints and not parts & set(skeleton.names):
        raise AlbamCheckFailure(
            "The motion drives none of this armature's bones",
            details=f"{vfile.display_name} keys bone ids {sorted(parts)}; "
                    f"{armature.name} has none of them.",
            solution="Pick the armature of the character the motion belongs to.",
        )
    if skipped_joints:
        print(f"[re4uhd] WARNING: {vfile.display_name}: skipped {len(skipped_joints)} joint(s) "
              f"that drive no bone: {'; '.join(skipped_joints)}")

    num_frames = fcv.max_frame + 1
    worlds, skipped_limbs = evaluate_motion(
        joints, skeleton, _double_joints(armature, skeleton), num_frames)
    for limb in skipped_limbs:
        print(f"[re4uhd] WARNING: {vfile.display_name}: IK chain {limb.label} cannot be solved on "
              f"{armature.name} ({limb.problem}); its rotations are kept, its target is ignored")
    bases = _pose_bases(skeleton, armature, worlds, num_frames)

    action = bpy.data.actions.new(f"{armature.name}.{vfile.display_name}")
    action.use_fake_user = True
    _key_bases(action, armature, bases)
    action.use_frame_range = True
    action.frame_start = 1
    action.frame_end = max(1, num_frames)

    armature.animation_data_create()
    armature.animation_data.action = action
    if hasattr(armature.animation_data, "action_slot") and len(action.slots):
        armature.animation_data.action_slot = action.slots[0]
    # Nothing to export (yet), so there is no container object to return:
    # the action is the import.
    return None


def _filter_armatures(self, obj):
    return obj.type == 'ARMATURE'


@blender_registry.register_blender_prop_albam(name='import_options_fcv')
class ImportOptionsFCV(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(type=bpy.types.Object, poll=_filter_armatures)


@blender_registry.register_import_options_custom_draw_func(extension='fcv')
def draw_fcv_options(panel_instance, context):
    panel_instance.bl_label = "FCV Options"
    panel_instance.layout.prop(context.scene.albam.import_options_fcv, 'armature')


@blender_registry.register_import_options_custom_poll_func(extension='fcv')
def poll_fcv_options(panel_instance, context):
    return True


@blender_registry.register_import_operator_poll_func(extension='fcv')
def poll_import_operator_for_fcv(panel_class, context):
    return bool(context.scene.albam.import_options_fcv.armature)
