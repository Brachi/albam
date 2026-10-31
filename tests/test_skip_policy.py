"""The safeguard for deselecting by Blender version (see tests/skip_policy.py):
a deselected test isn't reported anywhere, so one gated past every Blender
CI tests would never run and nothing would say so."""
import os
import re

from tests.conftest import BLENDER_GATES

WORKFLOW = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows", "tests.yml")


def ci_blender_versions():
    with open(WORKFLOW) as f:
        found = re.findall(r'"bpy-version":\s*"(\d+)\.(\d+)', f.read())
    assert found, f"no bpy-version in {WORKFLOW}'s matrix"
    return {(int(major), int(minor)) for major, minor in found}


def test_every_blender_gated_test_runs_on_a_version_ci_tests(pytestconfig):
    versions = ci_blender_versions()
    gates = pytestconfig.stash.get(BLENDER_GATES, {})
    never_run = sorted(nodeid for nodeid, gate in gates.items()
                       if not any(version >= gate for version in versions))
    assert not never_run, (
        f"deselected on every Blender CI tests ({sorted(versions)}): {never_run}")
