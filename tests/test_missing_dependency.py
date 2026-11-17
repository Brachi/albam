"""Tests for albam/_missing_dependency.py (#370).

The helper turns a ModuleNotFoundError for a third-party dependency into an
ImportError that tells a source-zip install apart from a release build
whose bundled wheels did not install, based on the manifest's `wheels`.
"""
import ast

import pytest

from albam import _missing_dependency
from albam._missing_dependency import missing_dependency_hint
from tests.subprocess_script import run_script

SOURCE_MANIFEST = 'platforms = ["windows-x64", "linux-x64"]\nwheels = [\n]\n'
RELEASE_MANIFEST = (
    'platforms = ["windows-x64", "linux-x64"]\n'
    'wheels = [\n  "./wheels/fs-2.4.16-py2.py3-none-any.whl",\n]\n'
)


def _missing(name):
    ex = ModuleNotFoundError(f"No module named {name!r}")
    ex.name = name
    return ex


@pytest.fixture
def manifest(tmp_path):
    def write(text):
        path = tmp_path / "blender_manifest.toml"
        path.write_text(text)
        return path
    return write


def test_source_manifest_gives_the_source_zip_hint(manifest):
    hint = missing_dependency_hint(_missing("fs"), manifest(SOURCE_MANIFEST))

    message = str(hint)
    assert isinstance(hint, ImportError)
    assert "'fs'" in message
    assert "Download ZIP" in message
    assert "releases" in message


def test_release_manifest_gives_the_wheels_failed_hint(manifest):
    hint = missing_dependency_hint(_missing("bc7enc"), manifest(RELEASE_MANIFEST))

    message = str(hint)
    assert "'bc7enc'" in message
    assert "did not install" in message
    assert "windows-x64, linux-x64" in message
    assert "Download ZIP" not in message


def test_dotted_name_reports_the_top_level_package(manifest):
    hint = missing_dependency_hint(_missing("fs.path"), manifest(SOURCE_MANIFEST))

    assert "'fs'" in str(hint)


@pytest.mark.parametrize("suffix", ["", ".lib.typo"])
def test_albam_modules_pass_through(manifest, suffix):
    name = _missing_dependency.__package__ + suffix

    assert missing_dependency_hint(_missing(name), manifest(SOURCE_MANIFEST)) is None


def test_unreadable_manifest_passes_through(tmp_path):
    assert missing_dependency_hint(_missing("fs"), tmp_path / "missing.toml") is None


def test_shipped_manifest_is_the_source_one():
    # build_extension.py fills `wheels` in only in the release zip it builds.
    hint = missing_dependency_hint(_missing("fs"))

    assert "Download ZIP" in str(hint)


def test_import_albam_raises_the_hint_when_a_dependency_is_missing():
    # sys.modules[name] = None makes the import system report that module as
    # not found, reproducing a source-zip install's missing `fs` from a dev
    # venv that has it.
    output = run_script(
        """
        sys.modules["fs"] = None
        try:
            import albam
        except ImportError as ex:
            print((type(ex).__name__, str(ex), type(ex.__cause__).__name__))
        else:
            print("no error raised")
        """
    )
    exc_type, message, cause_type = ast.literal_eval(output)
    assert exc_type == "ImportError"
    assert "Download ZIP" in message
    assert cause_type == "ModuleNotFoundError"


def test_import_albam_keeps_internal_import_errors():
    output = run_script(
        """
        sys.modules["albam.vfs"] = None
        try:
            import albam
        except ImportError as ex:
            print((type(ex).__name__, ex.name, ex.__cause__ is None))
        """
    )
    assert ast.literal_eval(output) == ("ModuleNotFoundError", "albam.vfs", True)
