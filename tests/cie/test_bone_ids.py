"""_bone_ids_by_name: the export id a Blender bone gets written under.

CI-safe: no game data or scene state, just the pure id-assignment logic (see
albam/engines/cie/mesh.py).
"""
from albam.engines.cie.mesh import _bone_ids_by_name


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
