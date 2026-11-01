"""Importing a skeletal motion (.fcv) onto an imported RE4UHD armature.

An .fcv names no skeleton: its joints are bone ids (see
structs/re4-uhd-fcv.ksy), which is also what the .bin importer names an
armature's bones after, so a motion goes onto whichever armature the import
panel points at, the same way an MT Framework .lmt does.

The keys cannot be copied onto pose bones one for one. A limb is an IK
chain: the file keys the chain's root rotation and, on its end joint, a
target position in model space that the game's solver (game/ik.cpp in the
RE4 decompilation) bends the chain towards every frame. Its elbows and
knees are not in the file at all, and a target read as a bone translation
tears the limb off. Neither the bend axis per chain nor the toe and twist
corrections it applies have a Blender constraint that behaves the same. So
this evaluates every frame the way the game does - Hermite curves, the
forward pass, the solver, then the double-joint blends - and bakes the
result into one key per frame per moved bone. The clip plays as it does in
the game, at the cost of not being an IK rig that can be re-posed by hand.

Root motion (the character's own displacement over the clip, which the game
applies to the model rather than to a part) is applied to the armature's
root bones, so a walk walks.
"""
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
KIND_ROTATION = 0x02
KIND_TRANSLATION = 0x04
KIND_SCALE = 0x08
KIND_IK_ROOT = 0x30
KIND_IK_TOE = 0x20
KIND_IK_FOUR_JOINTS = 0x80
KIND_ROOT_ROTATION = 0x40

# A chain root's channel is the axis its chain bends about (IKInit).
IK_BEND_AXES = {
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

# Game space (Y up, model units) to an armature's (Z up, metres), the same
# swap and scale the .bin importer builds the bones with (mesh._yz_flip).
GAME_TO_BLENDER = Matrix((
    (GLOBAL_SCALE, 0.0, 0.0, 0.0),
    (0.0, 0.0, -GLOBAL_SCALE, 0.0),
    (0.0, GLOBAL_SCALE, 0.0, 0.0),
    (0.0, 0.0, 0.0, 1.0),
))
BLENDER_TO_GAME = GAME_TO_BLENDER.inverted()


def hermite_value(frames, keys, frame):
    """One curve's value at `frame`, as game/motion.cpp HermiteInterpolation
    computes it: the key's own value on a key, the last key's from there on,
    and in between the cubic Hermite over the segment's normalised time with
    the tangents unscaled."""
    if not frames:
        return 0.0
    if frame >= frames[-1]:
        return keys[-1].value
    for i in range(len(frames) - 1):
        f0, f1 = frames[i], frames[i + 1]
        if frame == f0:
            return keys[i].value
        if f0 < frame < f1:
            t = (frame - f0) / (f1 - f0)
            t2 = t * t
            t3 = t2 * t
            h01 = -2.0 * t3 + 3.0 * t2
            h11 = t3 - t2
            h10 = h11 - t2 + t
            h00 = 1.0 - h01
            values = keys[i].value * h00 + keys[i + 1].value * h01
            return values + keys[i].out_tangent * h10 + keys[i + 1].in_tangent * h11
    return keys[0].value


def _axes_value(joint, frame):
    return Vector([hermite_value(list(axis.frames), axis.keys, frame) for axis in joint.axes])


def _rotation_matrix(ang):
    """The game's RotMatrix: Rz * Ry * Rx, which is Blender's XYZ euler."""
    return Euler(ang, 'XYZ').to_matrix().to_4x4()


def _local_matrix(pos, ang, scale):
    """partsMatCalc: rotation, translation column, then the columns scaled."""
    m = _rotation_matrix(ang)
    m.translation = pos
    return m @ Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))


def _orientation_zx(z, x):
    """math_sub SetOrientationZX: a rotation whose Z axis is `z` and whose X
    axis is `x`, orthonormalised."""
    vz = z.normalized()
    vy = vz.cross(x.normalized()).normalized()
    vx = vy.cross(vz).normalized()
    return Matrix((vx, vy, vz)).transposed().to_4x4()


def _orientation_zy(z, y):
    """math_sub SetOrientationZY: Z axis `z`, Y axis `y`, orthonormalised."""
    vz = z.normalized()
    vx = y.normalized().cross(vz).normalized()
    vy = vz.cross(vx).normalized()
    return Matrix((vx, vy, vz)).transposed().to_4x4()


def _with_translation(m, t):
    m = m.copy()
    m.translation = t
    return m


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


class _Chain:
    """One IK chain as IKInit sets it up: which parts, the bone lengths, and
    the frame the solver bends in, all from the rest pose."""

    def __init__(self, skeleton, root, kind, channel):
        self.root = root
        self.joint = root + 1
        self.has_toe = bool(kind & KIND_IK_TOE)
        self.four_joints = bool(kind & KIND_IK_FOUR_JOINTS)
        # The joint whose distance from `joint` is the second bone. For the
        # four-joint chains (the arms) the solve spans two parts, so it is
        # the one after the effector.
        self.end = root + 3 if self.four_joints and self.has_toe else root + 2
        self.effector = root + 2
        parts = [root, root + 1, root + 2] + ([root + 3] if self.four_joints or self.has_toe else [])
        missing = [p for p in parts if p not in skeleton.names]
        self.valid = not missing and channel in IK_BEND_AXES
        if not self.valid:
            return
        rest = skeleton.rest_world
        self.root_length = (rest[root] - rest[self.joint]).length
        self.joint_length = (rest[self.joint] - rest[self.end]).length
        direction = rest[self.end] - rest[root]
        axis = IK_BEND_AXES[channel]
        # IKInit's "IK plane error": a bend axis lying along the rest
        # direction leaves no plane to bend in, and the game skips the chain.
        if direction.length == 0 or direction.normalized().cross(axis).length < 1e-6:
            self.valid = False
            return
        mtx = _orientation_zy(direction, axis)
        self.inv_mat = mtx.transposed()
        self.up_vector = mtx.to_3x3() @ Vector((1.0, 0.0, 0.0))
        # Twist history of the four-joint chains (motParts.ikAng): lets the
        # twist run past half a turn without flipping.
        self.twist_history = 0.0


class _Pose:
    """One frame of the parts, in game space: local and world matrices per
    bone id, plus the translation each part is posed with."""

    def __init__(self, skeleton, model_matrix):
        self.skeleton = skeleton
        self.model = model_matrix
        self.pos = {}
        self.ang = {}
        self.local = {}
        self.world = {}

    def parent_world(self, bone_id):
        parent_id = self.skeleton.parent[bone_id]
        return self.world[parent_id] if parent_id is not None else self.model

    def world_pass(self):
        for bone_id in self.skeleton.order:
            self.world[bone_id] = self.parent_world(bone_id) @ self.local[bone_id]

    def relocalise(self, bone_id):
        self.local[bone_id] = self.parent_world(bone_id).inverted_safe() @ self.world[bone_id]


def _ik_solve(chain, pose, root, joint, end):
    """ikCalc: bend root and joint so that `end` stays where it is, by the
    law of cosines in the chain's bend plane."""
    root_world = pose.world[root].translation
    end_world = pose.world[end].translation
    d = (root_world - end_world).length
    la, lb = chain.root_length, chain.joint_length
    ang1 = ang2 = 0.0
    if d < la + lb and d > 0:
        c1 = (la * la + d * d - lb * lb) / ((la + la) * d)
        c2 = (d * d + lb * lb - la * la) / ((d + d) * lb)
        ang1 = math.acos(max(-1.0, min(1.0, c1)))
        ang2 = math.acos(max(-1.0, min(1.0, c2)))
    axis = pose.world[root].to_3x3() @ chain.up_vector
    m = _orientation_zx(end_world - root_world, axis) @ chain.inv_mat
    pose.world[root] = _with_translation(
        m @ Matrix.Rotation(-ang1, 4, chain.up_vector), root_world)
    joint_world = pose.world[root] @ pose.pos[joint]
    pose.world[joint] = _with_translation(
        m @ Matrix.Rotation(ang2, 4, chain.up_vector), joint_world)


def _twist(chain, pose, part, toe):
    """IK_TWIST_ANGLE: how far the end part has turned about the forearm,
    measured against the vertical."""
    rel = pose.world[part].inverted_safe() @ pose.world[toe]
    a = rel.col[0].to_3d()
    b = rel.col[2].to_3d()
    c = a.cross(Vector((0.0, 1.0, 0.0)))
    if c.length == 0 or b.length == 0:
        return 0.0
    ang = c.angle(b)
    d = c.cross(b)
    if d.dot(a) < 0.0:
        ang = -ang
        if chain.twist_history > math.pi / 2:
            ang += math.tau
        else:
            chain.twist_history = ang
    else:
        if chain.twist_history < -math.pi / 2:
            ang -= math.tau
        else:
            chain.twist_history = ang
    return ang


def _apply_twist(pose, part, ang):
    """IK_TWIST_APPLY: turn a part about its own X axis in place."""
    world = pose.world[part]
    axis = world.col[0].to_3d()
    if axis.length == 0:
        return
    pose.world[part] = _with_translation(
        Matrix.Rotation(ang, 4, axis.normalized()) @ world, world.translation)


def _inverse_kinematics(chains, pose):
    """InverseKinematics, without the floor probe (there is no floor here,
    and with none the game leaves the targets as keyed)."""
    for chain in chains:
        root, joint, effector = chain.root, chain.joint, chain.effector
        if not chain.four_joints:
            target = pose.model @ pose.pos[effector]
            if chain.has_toe:
                # heel2toe: the target is where the toe goes; the heel is
                # placed so that it lands there.
                toe = effector + 1
                world = pose.model @ pose.local[effector]
                heel = target - world.to_3x3() @ pose.pos[toe]
                pose.world[effector] = _with_translation(world, heel)
                pose.relocalise(effector)
                pose.world[toe] = pose.world[effector] @ pose.local[toe]
            else:
                pose.world[effector] = _with_translation(pose.model @ pose.local[effector], target)
                pose.relocalise(effector)
            _ik_solve(chain, pose, root, joint, effector)
            pose.relocalise(root)
            pose.relocalise(joint)
            if chain.has_toe:
                rest = pose.skeleton.rest_world
                attached = pose.world[joint] @ (rest[effector] - rest[joint])
                pose.world[effector] = _with_translation(pose.world[effector], attached)
                pose.relocalise(effector)
                pose.pos[effector] = pose.local[effector].translation
                toe = effector + 1
                pose.local[toe] = _local_matrix(pose.pos[toe], pose.ang[toe], (1.0, 1.0, 1.0))
                pose.world[toe] = pose.world[effector] @ pose.local[toe]
            else:
                pose.relocalise(effector)
        else:
            # The arms: the hand is keyed in model space outright, and the
            # upper arm and elbow are solved to reach it.
            end = chain.end
            pose.world[end] = pose.model @ pose.local[end]
            pose.relocalise(end)
            if not chain.has_toe:
                continue
            _ik_solve(chain, pose, root, joint, end)
            pose.world[effector] = pose.world[joint] @ pose.local[effector]
            ang = _twist(chain, pose, effector, end)
            _apply_twist(pose, effector, ang * 0.5)
            _apply_twist(pose, joint, ang * 0.25)
            _apply_twist(pose, root, ang * 0.125)
            for part in (root, joint, effector, end):
                pose.relocalise(part)
            pose.pos[end] = pose.local[end].translation


def _double_joints(armature, skeleton):
    """(helper, a, b, percent) per line of the model's double-joint table,
    from whichever mesh deformed by `armature` carries one (see
    mesh.BONE_PAIRS_PROPERTY)."""
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or BONE_PAIRS_PROPERTY not in ob:
            continue
        deformed_by = ob.parent is armature or any(
            m.type == 'ARMATURE' and m.object is armature for m in ob.modifiers)
        if not deformed_by:
            continue
        flat = list(ob[BONE_PAIRS_PROPERTY])
        lines = [tuple(flat[i:i + 4]) for i in range(0, len(flat) - 3, 4)]
        return [line for line in lines if all(b in skeleton.names for b in line[:3])]
    return []


def _apply_double_joints(pose, lines, keyed):
    """The DblJnt pass at the end of MotionMove: a helper bone takes the
    rotation `percent` of the way between two others, unless the motion keys
    it itself."""
    for helper, bone_a, bone_b, percent in lines:
        if helper in keyed:
            continue
        qa = pose.world[bone_a].to_3x3().normalized().to_quaternion()
        qb = pose.world[bone_b].to_3x3().normalized().to_quaternion()
        rotation = qb.slerp(qa, percent / 100.0).to_matrix().to_4x4()
        pose.world[helper] = _with_translation(rotation, pose.world[helper].translation)


def evaluate_motion(fcv, skeleton, double_joints=()):
    """{bone id: [game world matrix per frame]} for frames 0..max_frame,
    covering every bone of `skeleton`."""
    joints = [j for j in fcv.joints if j.info.channel not in CAMERA_CHANNELS]
    root_position = next((j for j in joints if j.info.kind == KIND_ROOT_POSITION), None)
    root_rotation = next((j for j in joints if j.info.kind == KIND_ROOT_ROTATION), None)
    chains = []
    for j in sorted(joints, key=lambda j: j.parts_no):
        if j.info.kind not in (KIND_ROOT_POSITION, KIND_ROOT_ROTATION) and j.info.kind & KIND_IK_ROOT:
            chain = _Chain(skeleton, j.parts_no, j.info.kind, j.info.channel)
            if chain.valid:
                chains.append(chain)
    keyed = {j.parts_no for j in joints}
    origin_position = _axes_value(root_position, 0) if root_position else Vector()
    origin_rotation = _axes_value(root_rotation, 0) if root_rotation else Vector()

    result = {bone_id: [] for bone_id in skeleton.order}
    for frame in range(fcv.max_frame + 1):
        model = Matrix.Identity(4)
        if root_position or root_rotation:
            offset = _axes_value(root_position, frame) - origin_position if root_position else Vector()
            turn = _axes_value(root_rotation, frame) - origin_rotation if root_rotation else Vector()
            model = Matrix.Translation(offset) @ _rotation_matrix(turn)
        pose = _Pose(skeleton, model)
        scale = {}
        for bone_id in skeleton.order:
            pose.pos[bone_id] = skeleton.rest_local[bone_id].copy()
            pose.ang[bone_id] = Vector()
            scale[bone_id] = Vector((1.0, 1.0, 1.0))
        # MotionMoveCore, in its own order of tests.
        for j in joints:
            kind = j.info.kind
            part = j.parts_no
            if part not in skeleton.names or kind in (KIND_ROOT_POSITION, KIND_ROOT_ROTATION):
                continue
            if kind & KIND_ROTATION:
                pose.ang[part] = _axes_value(j, frame)
            elif kind & KIND_TRANSLATION:
                pose.pos[part] = _axes_value(j, frame)
            elif kind & KIND_SCALE:
                scale[part] = _axes_value(j, frame)
            elif kind & KIND_IK_ROOT:
                pose.ang[part] = _axes_value(j, frame)
        for bone_id in skeleton.order:
            pose.local[bone_id] = _local_matrix(pose.pos[bone_id], pose.ang[bone_id], scale[bone_id])
        pose.world_pass()
        if chains:
            _inverse_kinematics(chains, pose)
            pose.world_pass()
        _apply_double_joints(pose, double_joints, keyed)
        for bone_id in skeleton.order:
            result[bone_id].append(pose.world[bone_id])
    return result


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
    fcv = Re4UhdFcv.from_bytes(fcv_bytes)
    fcv._read()
    # Joints are read lazily (they are instances); reading them all here is
    # what turns a malformed entry into an error at import, not half-way
    # through the bake.
    for joint in fcv.joints:
        for axis in joint.axes:
            axis.keys
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
            solution="A few weapon motions ship with broken camera joints the game never reads; "
                     "those cannot be imported.",
        ) from error
    if fcv.num_joints and all(j.info.channel in CAMERA_CHANNELS for j in fcv.joints):
        raise AlbamCheckFailure(
            "This .fcv moves a camera, not a skeleton",
            details=f"{vfile.display_name}: every joint is on a camera channel.",
            solution="Camera motions are not supported yet.",
        )
    skeleton = _Skeleton(armature)
    parts = {j.parts_no for j in fcv.joints if j.info.channel not in CAMERA_CHANNELS}
    if parts and not parts & set(skeleton.names):
        raise AlbamCheckFailure(
            "The motion drives none of this armature's bones",
            details=f"{vfile.display_name} keys bone ids {sorted(parts)}; "
                    f"{armature.name} has none of them.",
            solution="Pick the armature of the character the motion belongs to.",
        )

    worlds = evaluate_motion(fcv, skeleton, _double_joints(armature, skeleton))
    num_frames = fcv.max_frame + 1
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
