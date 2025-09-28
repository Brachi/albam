import json
import zlib

import sys
from pathlib import Path

# XXX temp until proper script installation
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

OUT = "albam/engines/mtfw/defines/shader-objects.json"


def generate_mfx_entry_id(mfx_entry_name, mfx_entry_index):
    return (((zlib.crc32(mfx_entry_name.encode()) ^ 0xffffffff) & 0x000fffff) << 12) + mfx_entry_index


def dump_mfx(app_id, mfx_filepath):
    # XXX temp until proper script installation
    from ..structs.mfx import Mfx

    mfx = Mfx.from_file(mfx_filepath)

    try:
        with open(OUT) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    for i, entry_ptr in enumerate(mfx.entry_pointers):
        if i == mfx.num_entries - 1:  # XXX last entry seems corrupted
            break
        mfx_entry = entry_ptr.mfx_entry
        mfx_name = mfx_entry.name

        entry = data.setdefault(mfx_name, {"hash": None, "friendly_name": None, "apps": {}})
        if not entry["hash"]:
            entry["hash"] = ((zlib.crc32(mfx_name.encode()) ^ 0xffffffff) & 0x000fffff)
            entry["friendly_name"] = mfx_name.lower().replace("$", "")

        entry["apps"][app_id] = {
            "shader_object_index": mfx_entry.index,
        }

    with open(OUT, 'w') as w:
        json.dump(data, w, indent=2)

    with open(OUT + ".ksy", 'w') as w:
        w.write("enums:\n")
        w.write("  shader_object_hash:\n")
        for entry_name, values in data.items():
            mfx_hash = hex(values["hash"])
            kaitai_name = values["friendly_name"]
            w.write(f"    {mfx_hash}: {kaitai_name}\n")
    print(f"Written in {OUT} and {OUT}.ksy")


if __name__ == "__main__":
    # TODO: argparse
    mfx_app_id = sys.argv[1]
    mfx_filepath = sys.argv[2]
    dump_mfx(mfx_app_id, mfx_filepath)
