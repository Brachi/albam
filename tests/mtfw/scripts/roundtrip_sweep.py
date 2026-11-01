"""Parse every file of a given format in a game install and write it straight
back out, reporting which ones don't come back byte-identical.

This is the struct-level round trip: bytes -> kaitai object -> bytes, with no
Blender in the loop. It isolates a .ksy definition's fidelity from everything
import and export do on top - a mismatch here means the definition itself
loses or misrepresents something in the file, which is a different failure
class from what tests/mtfw/test_*_serialization.py tracks, and cheap enough
to run over a whole game.

What it has found so far, on .mod: face_offset being added to a mesh's index
buffer position, which made 9 umvc3 and 38 re6 models unreadable, and
confirmed the fix afterwards across all 2702 umvc3 models.

Maintainer/owner tool, not part of CI: it needs a real game install, and a
full sweep takes minutes even parallelised.

Usage (from the repo root, with a bpy-enabled interpreter):

    python tests/mtfw/scripts/roundtrip_sweep.py <app-id> <game-root>
        [--format mod|tex|rtex|sbc|mrl|lmt|nav|all] [--pattern REGEX]
        [--jobs N] [--limit N] [--ignore-nan-payload] [--out results.json]

Two things worth knowing before reading a result:

Floats holding NaN do not survive a round trip. Python normalises a
signalling NaN to a quiet one, setting bit 22, so the byte differs by 0x40
and nothing else. 433 of re5's 3467 .mod differ for exactly this reason and
no other, from uninitialised padding in weight_bound vectors. Pass
--ignore-nan-payload to treat a difference as benign when every differing
byte satisfies new == old | 0x40.

A format that does not round trip is not automatically broken. Where a value
is derived rather than stored - a strip length, say - a re-encode can
legitimately differ. Check what a mismatch means before treating it as a bug.

Note on lazy instances: parsing does not materialise kaitai "instances", so
_write() raises AttributeError on the private _m_<name> attribute unless
_fetch_instances() runs first. That is the read-write API's contract, not a
struct bug.
"""
import argparse
import collections
import json
import multiprocessing
import os
import re
import sys
import time
import traceback

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, _REPO_ROOT)

# One MTFW_FS per worker process, built once in _init_worker: scanning a whole
# install takes ~10s, so building it per file would dominate, and the instance
# cannot be pickled across to the workers anyway.
_WORKER_STATE = {}

# extension -> how to get the struct class for an app_id. Every format albam
# models per-app already keeps such a mapping next to its own code; this
# borrows them rather than restating which app uses which version, so a new
# app_id needs no change here.
FORMATS = ("mod", "tex", "rtex", "sbc", "mrl", "lmt", "nav")

# Bit 22 of a float32, the quiet-NaN flag. A signalling NaN read and written
# back comes out quiet, which is the only way a round trip alters a byte
# without anything being lost - see the module docstring.
QUIET_NAN_BIT = 0x40


def _struct_class(fmt, app_id):
    """(class, extra constructor params) for a format and app, or None if the
    app has no struct for it."""
    from albam.engines.mtfw.structs.lmt import Lmt
    from albam.engines.mtfw.structs.mrl import Mrl
    from albam.engines.mtfw.structs.nav_156 import Nav156

    if fmt == "mod":
        from albam.engines.mtfw.mesh import APPID_CLASS_MAPPER
        cls = APPID_CLASS_MAPPER.get(app_id)
    elif fmt == "tex":
        from albam.engines.mtfw.texture import APPID_TEXCLS_MAP
        cls = APPID_TEXCLS_MAP.get(app_id)
    elif fmt == "rtex":
        from albam.engines.mtfw.texture import APPID_RTEXCLS_MAP
        cls = APPID_RTEXCLS_MAP.get(app_id)
    elif fmt == "sbc":
        from albam.engines.mtfw.collision import APPID_SBC_CLASS_MAPPER
        cls = APPID_SBC_CLASS_MAPPER.get(app_id)
    elif fmt == "mrl":
        cls = Mrl
    elif fmt == "lmt":
        cls = Lmt
    elif fmt == "nav":
        cls = Nav156
    else:
        return None
    if cls is None:
        return None
    # Some structs take app_id, some do not - the signature is the authority.
    import inspect
    takes_app_id = "app_id" in inspect.signature(cls.__init__).parameters
    return cls, ((app_id,) if takes_app_id else ())


def _init_worker(app_id, game_root, formats):
    from albam.engines.mtfw.arc_fs import MTFW_FS

    _WORKER_STATE["fs"] = MTFW_FS(game_root)
    _WORKER_STATE["app_id"] = app_id
    _WORKER_STATE["classes"] = {f: _struct_class(f, app_id) for f in formats}


def _first_difference(a, b):
    """Offset of the first differing byte, or the shorter length if one is a
    prefix of the other. The offset points straight at the field in the .ksy."""
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b))


def _only_quiet_nan(original, written):
    """Whether every differing byte is the quiet-NaN flag being set."""
    if len(original) != len(written):
        return False
    return all(new == old | QUIET_NAN_BIT
               for old, new in zip(original, written) if old != new)


def _roundtrip(item):
    from kaitaistruct import BytesIO, KaitaiStream

    from albam.lib.kaitai_utils import check_recursive, parse

    fmt, path = item
    entry = _WORKER_STATE["classes"].get(fmt)
    if entry is None:
        return {"path": path, "format": fmt, "result": "unsupported"}
    cls, params = entry
    fs = _WORKER_STATE["fs"]
    try:
        with fs.openbin(path) as f:
            data = f.read()
    except Exception as e:
        return {"path": path, "format": fmt, "result": "unreadable",
                "error": f"{type(e).__name__}: {e}"}

    try:
        obj = parse(cls, data, *params)
        obj._fetch_instances()
        check_recursive(obj)
        stream = KaitaiStream(BytesIO(bytearray(len(data))))
        obj._write(stream)
        out = stream.to_byte_array()
    except Exception as e:
        return {"path": path, "format": fmt, "result": "error", "size": len(data),
                "error": f"{type(e).__name__}: {e}",
                "traceback": traceback.format_exc(limit=3)}

    if out == data:
        return {"path": path, "format": fmt, "result": "identical", "size": len(data)}
    if _WORKER_STATE.get("ignore_nan") and _only_quiet_nan(data, out):
        return {"path": path, "format": fmt, "result": "identical_modulo_nan",
                "size": len(data)}
    return {"path": path, "format": fmt, "result": "differs", "size": len(data),
            "size_out": len(out), "first_diff": _first_difference(data, out),
            "only_quiet_nan": _only_quiet_nan(data, out)}


def _init_worker_with_flags(app_id, game_root, formats, ignore_nan):
    _init_worker(app_id, game_root, formats)
    _WORKER_STATE["ignore_nan"] = ignore_nan


def category(path):
    """Top-level directory, which is how installs group content (chr/, stg/,
    ui/, eft/ for umvc3) - the useful axis to report on, since coverage and
    behaviour both vary by it."""
    parts = path.lstrip("/").split("/")
    return parts[0] if parts else "?"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("app_id")
    parser.add_argument("game_root")
    parser.add_argument("--format", default="mod",
                        choices=(*FORMATS, "all"),
                        help="which format to sweep (default: mod)")
    parser.add_argument("--pattern", default=None, help="regex to filter paths")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    parser.add_argument("--ignore-nan-payload", action="store_true",
                        help="count a file as identical when every differing byte is "
                             "only the quiet-NaN flag being set (see the module docstring)")
    parser.add_argument("--out", default=None, help="write full results as JSON")
    args = parser.parse_args()

    formats = list(FORMATS) if args.format == "all" else [args.format]
    from albam.engines.mtfw.arc_fs import MTFW_FS

    t0 = time.time()
    all_paths = list(MTFW_FS(args.game_root).walk.files())
    items = []
    for fmt in formats:
        suffix = "." + fmt
        items.extend((fmt, p) for p in sorted(all_paths) if p.lower().endswith(suffix))
    if args.pattern:
        rx = re.compile(args.pattern, re.IGNORECASE)
        items = [it for it in items if rx.search(it[1])]
    if args.limit:
        items = items[:args.limit]
    per_fmt = collections.Counter(f for f, _p in items)
    print(f"indexed {len(items)} file(s) in {time.time() - t0:.1f}s "
          f"({dict(per_fmt)}), {args.jobs} worker(s)", file=sys.stderr, flush=True)
    if not items:
        print("nothing to sweep")
        return 0

    t0 = time.time()
    results = []
    with multiprocessing.Pool(
            args.jobs, initializer=_init_worker_with_flags,
            initargs=(args.app_id, args.game_root, formats, args.ignore_nan_payload)) as pool:
        for i, res in enumerate(pool.imap_unordered(_roundtrip, items, chunksize=8), 1):
            results.append(res)
            if i % 500 == 0:
                bad = sum(1 for r in results if r["result"] in ("differs", "error"))
                print(f"  {i}/{len(items)} bad={bad} {time.time() - t0:.0f}s",
                      file=sys.stderr, flush=True)
    elapsed = time.time() - t0

    print(f"\nswept {len(results)} file(s) in {elapsed:.0f}s "
          f"({elapsed / max(len(results), 1):.3f}s/file, {args.jobs} workers)")
    by_fmt = collections.defaultdict(collections.Counter)
    for r in results:
        by_fmt[r["format"]][r["result"]] += 1
    for fmt in sorted(by_fmt):
        row = by_fmt[fmt]
        detail = "  ".join(f"{k}={v}" for k, v in sorted(row.items()))
        print(f"  {fmt + ':':6} total={sum(row.values()):6}  {detail}")

    bad = [r for r in results if r["result"] in ("differs", "error")]
    if bad:
        by_cat = collections.defaultdict(collections.Counter)
        for r in bad:
            by_cat[category(r["path"])][r["format"]] += 1
        print("\nnot identical, by category:")
        for cat in sorted(by_cat):
            print(f"  {cat + '/':10} {dict(by_cat[cat])}")
        nan_only = sum(1 for r in bad if r.get("only_quiet_nan"))
        if nan_only:
            print(f"\n{nan_only} of {len(bad)} differ only by the quiet-NaN flag "
                  f"(--ignore-nan-payload treats these as identical)")
        print(f"\nfirst {min(len(bad), 15)} of {len(bad)}:")
        for r in bad[:15]:
            if r["result"] == "differs":
                print(f"  {r['format']:5} {r['path']}  in={r['size']} out={r['size_out']} "
                      f"first_diff=0x{r['first_diff']:x}")
            else:
                print(f"  {r['format']:5} {r['path']}  {r['error'][:100]}")
        errors = collections.Counter(
            r["error"].split(":")[0] for r in bad if r["result"] == "error")
        if errors:
            print("\nerror types:", dict(errors.most_common(8)))

    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nwrote {args.out}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
