"""_bone_ids_by_name: the export id a Blender bone gets written under, and
which bones that id space has to cover.

CI-safe: no game data or scene state, just the pure id-assignment logic (see
albam/engines/cie/mesh.py).
"""
import pytest

from albam.engines.cie.mesh import (_bone_ids_by_name, _bones_to_write,
                                    _serialize_bones)
from albam.exceptions import AlbamCheckFailure


class _FakeBone:
    def __init__(self, name):
        self.name = name


def test_ids_follow_name_or_armature_position():
    bones = [_FakeBone(n) for n in ("root", "spine", "head")]
    assert _bone_ids_by_name(bones) == {"root": 0, "spine": 1, "head": 2}


def test_a_digit_name_claims_its_own_id_outright():
    bones = [_FakeBone("root"), _FakeBone("5"), _FakeBone("head")]
    ids = _bone_ids_by_name(bones)
    assert ids["5"] == 5


def test_a_fallback_id_colliding_with_a_digit_name_is_not_dropped():
    """A hand-added bone whose armature position matches a digit-named bone
    elsewhere used to collide with it silently: both bones would map to the
    same id, and whichever _bones_to_write met first hid the other one
    entirely from the exported table.
    """
    bones = [_FakeBone("5"), _FakeBone("a"), _FakeBone("b"),
             _FakeBone("c"), _FakeBone("d"), _FakeBone("e")]
    ids = _bone_ids_by_name(bones)

    assert len(set(ids.values())) == len(ids), f"id collision in {ids}"
    assert ids["5"] == 5
    assert ids["e"] != 5


def test_every_id_stays_within_the_format_s_u1_ceiling():
    bones = [_FakeBone(str(i)) for i in range(200, 260)]
    ids = _bone_ids_by_name(bones)
    assert all(0 <= bone_id <= 254 for bone_id in ids.values())


def test_a_zero_padded_name_does_not_claim_an_id_a_second_time():
    """"05" and "5" spell the same id, so letting both claim it dropped one
    of the two bones from the exported table while its weights re-mapped
    onto the survivor.
    """
    bones = [_FakeBone("5"), _FakeBone("05"), _FakeBone("head")]
    ids = _bone_ids_by_name(bones)

    assert len(set(ids.values())) == len(ids), f"id collision in {ids}"
    assert ids["5"] == 5


def test_a_bone_with_no_free_id_left_gets_none_rather_than_a_duplicate():
    """Nudging a fallback used to stop at 254 and hand it out anyway, which
    is the very duplicate this function exists to prevent. A bone past the
    255 the format can name is left out of the mapping instead - it only
    matters if the model actually writes it (see _serialize_bones).
    """
    bones = [_FakeBone(str(i)) for i in range(255)] + [_FakeBone("extra")]

    ids = _bone_ids_by_name(bones)

    assert len(set(ids.values())) == len(ids), f"id collision in {ids}"
    assert "extra" not in ids
    assert len(ids) == 255


def test_a_model_bound_to_the_upper_half_of_a_rig_still_gets_an_id():
    """An armature can hold only the upper part of a shared rig (see
    _bones_to_write), leaving every id below it free. Nudging upward alone
    ran out at 254 and errored while those lower ids were still available.
    """
    bones = [_FakeBone(str(i)) for i in range(60, 255)] + [_FakeBone("helper")]

    ids = _bone_ids_by_name(bones)

    assert len(set(ids.values())) == len(ids), f"id collision in {ids}"
    assert ids["helper"] < 60


class _FakeArmature:
    def __init__(self, bones):
        self.name = "Armature"
        self.data = type("_Data", (), {"bones": bones})()


class _FakeBoneWithParent(_FakeBone):
    def __init__(self, name, parent=None):
        super().__init__(name)
        self.parent = parent

    @property
    def parent_recursive(self):
        return [self.parent] + self.parent.parent_recursive if self.parent else []


def test_bones_nothing_writes_do_not_have_to_fit_in_the_format_s_id_space():
    """A rig can carry far more bones than a .bin can name - control and IK
    bones nothing is weighted to, say - and only the ones the model writes
    ever reach the file (see _bones_to_write). Assigning ids over the whole
    armature made such a rig refuse to export over bones no table would have
    held.
    """
    weighted = _FakeBoneWithParent("7")
    bones = [weighted] + [_FakeBoneWithParent(f"control_{i}") for i in range(300)]
    armature = _FakeArmature(bones)

    ids = _bone_ids_by_name(bones)
    written = _bones_to_write(armature, ids, used_ids=(7,))

    assert [bone.name for bone in written] == ["7"]
    assert all(bone.name in ids for bone in written)


def test_writing_a_bone_the_format_cannot_name_fails_with_a_clear_error():
    """The id space only has to cover what reaches the file, but a model that
    does write more bones than the format can name has to say so rather than
    write a table with bones missing.
    """
    bones = [_FakeBoneWithParent(f"bone_{i}") for i in range(300)]

    with pytest.raises(AlbamCheckFailure) as raised:
        _serialize_bones(None, _FakeArmature(bones))

    assert raised.value.details
    assert raised.value.solution
