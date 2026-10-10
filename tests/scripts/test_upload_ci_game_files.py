"""Covers upload_ci_game_files.py's decision layer - which app_ids may be
uploaded for, and which hashes an upload would cover.

CI-safe: every test here reads committed files only. Nothing touches a game
install, R2, or bpy, which is exactly why the script defers its albam import
until resolution time (see the comment there).
"""
import json
import os

import pytest

from tests.scripts import upload_ci_game_files as uploader

WORKFLOW = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".github", "workflows", "tests.yml",
)


def test_ci_app_ids_matches_the_workflow():
    """The workflow is the source of truth for what CI mounts. If this fails
    after a workflow edit, the upload gate is about to allow (or refuse) a
    different set of app_ids - which is the point, but worth noticing.
    """
    assert uploader.ci_app_ids(WORKFLOW) == {"re5", "re1", "umvc3", "re4uhd", "reorc"}


def test_ci_app_ids_ignores_the_shell_expression_in_the_value():
    """--game-dir's value in CI is a shell expression, not a literal - only
    the app-id before '::' may be read out of it.
    """
    workflow = 'run: pytest --game-dir=re5::r2://"$R2_BUCKET_NAME"/re5 --game-dir=re1::/local\n'
    path = os.path.join(os.path.dirname(__file__), "_tmp_workflow.yml")
    with open(path, "w") as f:
        f.write(workflow)
    try:
        assert uploader.ci_app_ids(path) == {"re5", "re1"}
    finally:
        os.remove(path)


def test_dataset_hashes_are_collected_per_app():
    hashes = uploader.dataset_hashes_for("re5")
    assert hashes, "re5 is referenced by committed datasets"
    # Every value names the dataset(s) that referenced it, and every hash is
    # the 16-char truncated digest catalog_paths produces.
    for path_hash, sources in hashes.items():
        assert len(path_hash) == 16
        assert sources and all(s.endswith("_hashes.json") for s in sources)


def test_dataset_hashes_for_unknown_app_is_empty():
    assert uploader.dataset_hashes_for("not-a-real-app") == {}


def test_each_app_id_is_claimed_by_exactly_one_engine():
    """An app_id in two engines' APP_IDS would resolve against whichever
    module happens to be listed first, silently uploading the wrong files.
    """
    claimed = [app_id for source in uploader.UPLOAD_SOURCES for app_id in source.APP_IDS]
    assert len(claimed) == len(set(claimed))


def test_dataset_hashes_are_collected_for_every_engine():
    """Each engine's datasets are found through its own module, so a source
    pointed at the wrong directory shows up here rather than as an empty
    upload."""
    for source in uploader.UPLOAD_SOURCES:
        assert any(uploader.dataset_hashes_for(app_id) for app_id in source.APP_IDS), (
            f"no committed dataset references any app_id of {source.__name__}")


@pytest.mark.parametrize("app_id", ["re6"])
def test_app_id_not_in_ci_uploads_nothing(app_id, capsys):
    """The behaviour this tool exists to enforce: an app_id CI never mounts
    is refused before any credential, install or network access, and the
    message names the flag that would make it uploadable.
    """
    exit_code = uploader.main([
        "--app-id", app_id, "--game-root", os.path.dirname(__file__),
    ])
    assert exit_code == 2
    err = capsys.readouterr().err
    assert "NOTHING UPLOADED" in err
    assert f"--game-dir={app_id}::" in err


def test_app_id_in_ci_passes_the_gate(capsys):
    """re5 is mounted by CI, so the gate lets it through - it stops later,
    on the game root, rather than on the app_id itself.
    """
    exit_code = uploader.main([
        "--app-id", "re5", "--game-root", "/definitely/not/here", "--dry-run",
    ])
    assert exit_code == 2
    err = capsys.readouterr().err
    assert "is not a directory" in err
    assert "CI does not run" not in err


def test_every_dataset_hash_is_in_the_catalog():
    """Mirrors test_dataset_hashes_are_in_catalog in the suite, for the
    app_ids this tool can actually upload: resolving an upload set against a
    hash missing from the catalog would bake that disagreement into R2.
    """
    for app_id in uploader.ci_app_ids(WORKFLOW):
        source = uploader.upload_source_for(app_id)
        catalog_path = os.path.join(source.DATASETS_DIR, f"{app_id}_catalog.json")
        if not os.path.isfile(catalog_path):
            continue
        with open(catalog_path) as f:
            catalog = {e["path_hash"] for e in json.load(f)}
        for path_hash, sources in uploader.dataset_hashes_for(app_id).items():
            assert path_hash in catalog, f"{path_hash} ({sources}) missing from {app_id} catalog"


def test_refusal_still_reports_the_upload_size(tmp_path, monkeypatch, capsys):
    """An app_id CI doesn't run still gets sized: the number is the point of
    the report - it says what enabling that app_id in CI would cost - so it
    has to survive the refusal rather than being skipped along with it.

    Resolution itself is faked; it needs a real game install and bpy, and
    what's under test here is the reporting around it, not MTFW_FS.
    """
    archive = tmp_path / "nativePC" / "one.arc"
    archive.parent.mkdir(parents=True)
    archive.write_bytes(b"x" * 4096)

    monkeypatch.setattr(
        uploader, "resolve_upload_set",
        lambda game_root, app_id, hashes: ({str(archive): "nativePC/one.arc"}, hashes),
    )

    exit_code = uploader.main([
        "--app-id", "re6", "--game-root", str(tmp_path),
    ])
    assert exit_code == 2

    captured = capsys.readouterr()
    assert "4.0KiB" in captured.out          # itemised in the report
    assert "4.0KiB" in captured.err          # and restated in the refusal
    assert "would be uploaded if it did" in captured.err
    assert "NOTHING UPLOADED" in captured.err


def test_unresolvable_game_root_downgrades_to_an_unsized_refusal(capsys):
    """Sizing failures are only fatal when an upload could have followed.
    For an app_id CI doesn't run there was never going to be one, so a game
    root that can't be resolved against still produces the refusal.
    """
    exit_code = uploader.main([
        "--app-id", "re6", "--game-root", "/definitely/not/here",
    ])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "upload size unknown" in captured.out
    assert "The upload size could not be computed." in captured.err
    assert "NOTHING UPLOADED" in captured.err


# --- upload/delete against a mocked bucket -------------------------------
# re5 is used throughout below because it is an app_id CI runs: anything
# else is refused before reaching the code under test here.

boto3 = pytest.importorskip("boto3")
mock_aws = pytest.importorskip("moto").mock_aws

BUCKET = "albam-test"


@pytest.fixture
def fake_game_files(tmp_path, monkeypatch):
    """Stands in for resolving hashes against a real install: writes two
    files and points the uploader at them, so these tests exercise the
    upload/delete decisions rather than MTFW_FS.
    """
    arc = tmp_path / "nativePC" / "one.arc"
    arc.parent.mkdir(parents=True)
    arc.write_bytes(b"a" * 2048)
    loose = tmp_path / "loose.tex"
    loose.write_bytes(b"b" * 512)

    uploads = {str(arc): "nativePC/one.arc", str(loose): "loose.tex"}
    monkeypatch.setattr(
        uploader, "resolve_upload_set",
        lambda game_root, app_id, hashes: (uploads, hashes),
    )
    monkeypatch.setattr(
        uploader, "r2_credentials",
        lambda: {"aws_access_key_id": "test", "aws_secret_access_key": "test"},
    )
    return tmp_path, arc, loose


def run_uploader(game_root, *extra):
    return uploader.main([
        "--app-id", "re5", "--game-root", str(game_root),
        "--bucket", BUCKET, "--yes", *extra,
    ])


@pytest.fixture
def s3():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        yield client


def test_upload_stores_a_checksum(fake_game_files, s3):
    game_root, arc, _loose = fake_game_files
    assert run_uploader(game_root) == 0

    head = s3.head_object(Bucket=BUCKET, Key="re5/nativePC/one.arc")
    assert head["ContentLength"] == 2048
    assert head["Metadata"][uploader.CHECKSUM_METADATA_KEY] == uploader.file_checksum(str(arc))


def test_unchanged_files_are_skipped(fake_game_files, s3, capsys):
    game_root, _arc, _loose = fake_game_files
    assert run_uploader(game_root) == 0
    capsys.readouterr()

    assert run_uploader(game_root) == 0
    out = capsys.readouterr().out
    assert "2 unchanged (checksum verified)" in out
    assert "nothing to do" in out


def test_same_size_different_content_is_re_uploaded(fake_game_files, s3, capsys):
    """The case a size-only comparison gets wrong. An .arc repacked from the
    same entries can keep its exact length; skipping it would leave CI
    reading stale bytes with nothing to signal it.
    """
    game_root, arc, _loose = fake_game_files
    assert run_uploader(game_root) == 0
    capsys.readouterr()

    arc.write_bytes(b"c" * 2048)  # same length, different bytes
    assert run_uploader(game_root) == 0

    out = capsys.readouterr().out
    assert "1 unchanged (checksum verified)" in out
    assert "uploading 1 file(s)" in out
    assert s3.get_object(Bucket=BUCKET, Key="re5/nativePC/one.arc")["Body"].read() == b"c" * 2048


def test_object_without_a_checksum_is_assumed_unchanged_by_size(fake_game_files, s3, capsys):
    """Objects predating this tool have no stored checksum, so size is all
    there is to go on - reported as assumed, never as verified.
    """
    game_root, _arc, _loose = fake_game_files
    s3.put_object(Bucket=BUCKET, Key="re5/nativePC/one.arc", Body=b"z" * 2048)
    s3.put_object(Bucket=BUCKET, Key="re5/loose.tex", Body=b"z" * 512)

    assert run_uploader(game_root) == 0
    out = capsys.readouterr().out
    assert "2 assumed unchanged (same size, no stored checksum" in out
    assert "checksum verified" not in out


def test_force_re_uploads_everything(fake_game_files, s3, capsys):
    game_root, _arc, _loose = fake_game_files
    assert run_uploader(game_root) == 0
    capsys.readouterr()

    assert run_uploader(game_root, "--force") == 0
    assert "uploading 2 file(s)" in capsys.readouterr().out


def test_delete_prunes_only_unreferenced_objects(fake_game_files, s3, capsys):
    game_root, _arc, _loose = fake_game_files
    assert run_uploader(game_root) == 0
    s3.put_object(Bucket=BUCKET, Key="re5/nativePC/gone.arc", Body=b"old")
    # A different app's prefix must never be touched by re5's own prune.
    s3.put_object(Bucket=BUCKET, Key="re1/nativePC/other.arc", Body=b"other")
    capsys.readouterr()

    assert run_uploader(game_root, "--delete") == 0
    out = capsys.readouterr().out
    assert "1 stale object(s) under re5/" in out
    assert "re5/nativePC/gone.arc" in out

    keys = {o["Key"] for o in s3.list_objects_v2(Bucket=BUCKET)["Contents"]}
    assert keys == {"re5/nativePC/one.arc", "re5/loose.tex", "re1/nativePC/other.arc"}


def test_delete_dry_run_deletes_nothing(fake_game_files, s3, capsys):
    game_root, _arc, _loose = fake_game_files
    assert run_uploader(game_root) == 0
    s3.put_object(Bucket=BUCKET, Key="re5/nativePC/gone.arc", Body=b"old")
    capsys.readouterr()

    assert run_uploader(game_root, "--delete", "--dry-run") == 0
    out = capsys.readouterr().out
    assert "--dry-run: nothing uploaded or deleted" in out
    assert s3.head_object(Bucket=BUCKET, Key="re5/nativePC/gone.arc")["ContentLength"] == 3
