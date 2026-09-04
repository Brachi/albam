"""
Guards on the Kaitai Struct toolchain itself, rather than on any one
format: the .ksy sources have to keep compiling, and the generated code
has to keep exposing the handful of names albam assigns to by hand.

Both failures this protects against are silent. A .ksy that no longer
compiles is only noticed by whoever next tries to regenerate it, and a
renamed attribute on a generated class is not an error in Python at all -
`mesh.vertices__enabled = False` against a class that has since renamed
that attribute just creates a new one and writes the buffer anyway. That
rename has already happened once, between the 0.11 pre-release and the
0.11 release (`__to_write` -> `__enabled`).
"""
import os
import shutil
import subprocess

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINES_DIR = os.path.join(REPO_ROOT, "albam", "engines")
COMPILER = "kaitai-struct-compiler"

# Names albam assigns to on a generated Mesh to keep a lazily-written
# buffer from being serialized twice (albam/engines/mtfw/mesh.py). Listed
# per app_id because they only exist for fields the format actually has -
# mod 21 has no second vertex buffer, so nothing there defines
# `vertices2__enabled`, and albam's unconditional assignment to it is a
# no-op for that version.
WRITE_CONTROL_ATTRS = {
    "re5": ("indices__enabled", "vertices__enabled", "vertices2__enabled"),
    "re1": ("indices__enabled", "vertices__enabled"),
}

# Every parser is generated with `-w`/`--read-write`, including the formats
# albam only reads today, so there is one regeneration command rather than a
# per-file split nothing in the .ksy records. The cost is that `-w` implies
# `--no-auto-read`: constructing a parser no longer parses anything, and
# every caller has to follow it with an explicit `_read()`.


def _ksy_files():
    found = []
    for root, _, files in os.walk(ENGINES_DIR):
        found.extend(os.path.join(root, f) for f in files if f.endswith(".ksy"))
    return sorted(found)


def test_ksy_files_are_found():
    """Guards the two tests below against silently passing on an empty set
    if the structs ever move."""
    assert len(_ksy_files()) > 15


@pytest.mark.skipif(shutil.which(COMPILER) is None, reason=f"{COMPILER} not installed")
def test_every_ksy_file_compiles(tmp_path):
    """`ks-version: 0.10` unquoted is read by YAML as the float 0.1, which
    the compiler rejects as below its minimum supported version - so a
    struct can stop compiling without anything in the repo changing. Quoted
    versions avoid it; this keeps them that way.
    """
    result = subprocess.run(
        [COMPILER, "--target", "python", "-w", "--outdir", str(tmp_path), *_ksy_files()],
        capture_output=True,
        text=True,
    )
    errors = [ln for ln in (result.stdout + result.stderr).splitlines() if "error" in ln.lower()]
    assert not errors, "\n".join(errors)
    assert result.returncode == 0


@pytest.mark.parametrize("app_id", sorted(WRITE_CONTROL_ATTRS))
def test_generated_meshes_keep_their_write_control_attributes(app_id):
    """albam/engines/mtfw/mesh.py turns off lazy writing for buffers it
    serializes itself by assigning to `<field>__enabled`. The compiler has
    renamed these once already (`__to_write` before the 0.11 release), and
    because assigning an unknown attribute is legal Python, a rename would
    leave export running while silently writing those buffers twice. Fail
    here instead.
    """
    from albam.engines.mtfw.mesh import APPID_CLASS_MAPPER
    from kaitaistruct import BytesIO, KaitaiStream

    mesh = APPID_CLASS_MAPPER[app_id].Mesh(KaitaiStream(BytesIO(b"")), None, None)
    missing = [name for name in WRITE_CONTROL_ATTRS[app_id] if not hasattr(mesh, name)]
    assert not missing, (
        f"{APPID_CLASS_MAPPER[app_id].__name__}.Mesh no longer defines {missing}. If the structs "
        f"were regenerated, update both these names and the assignments in mtfw/mesh.py together."
    )


def _generated_parsers():
    found = []
    for root, _, files in os.walk(ENGINES_DIR):
        if os.path.basename(root) != "structs":
            continue
        for name in files:
            if name.endswith(".py") and name != "__init__.py":
                found.append(os.path.relpath(os.path.join(root, name), REPO_ROOT))
    return sorted(found)


def test_every_parser_is_generated_read_write():
    """One regeneration command for the whole tree, so nothing depends on
    remembering which formats albam happens to serialize today. A parser
    regenerated without `-w` still imports and still reads - it just has no
    `_write()`, so exporting that format breaks whenever someone adds it.
    """
    read_only = []
    for parser in _generated_parsers():
        with open(os.path.join(REPO_ROOT, parser)) as f:
            if "_write__seq" not in f.read():
                read_only.append(parser)
    assert not read_only, (
        "generated without -w/--read-write:\n  " + "\n  ".join(read_only)
    )
