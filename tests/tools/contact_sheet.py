"""Tile a directory of renders into one contact sheet, so a sweep's output
can be reviewed at a glance instead of opened file by file.

Uses Blender's own image API rather than an imaging library: bpy is already
a dependency of everything else in this directory, and adding Pillow just to
paste rectangles isn't worth it.

Usage (from the repo root, with a bpy-enabled interpreter):

    python tests/tools/contact_sheet.py <png-dir> <output.png>
                                 [--columns N] [--cell N] [--pattern GLOB]

Example:

    python tests/tools/contact_sheet.py tests/data/re4uhd sheet.png --columns 12
"""
import argparse
import fnmatch
import os
import sys

import bpy

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _REPO_ROOT)


def _load_scaled(path, cell):
    """One render as a cell-sized RGBA float list, letterboxed to square."""
    image = bpy.data.images.load(path)
    try:
        image.scale(cell, cell)
        return list(image.pixels)
    finally:
        bpy.data.images.remove(image)


def build_sheet(paths, output_path, columns, cell):
    rows = (len(paths) + columns - 1) // columns
    width, height = columns * cell, rows * cell
    # Blender images are bottom-up, so row 0 of the sheet is the last row of
    # the buffer; the tiles are placed accordingly rather than flipped after.
    buffer = [0.14, 0.14, 0.16, 1.0] * (width * height)

    for index, path in enumerate(paths):
        pixels = _load_scaled(path, cell)
        column = index % columns
        row = rows - 1 - index // columns
        for y in range(cell):
            source = y * cell * 4
            target = ((row * cell + y) * width + column * cell) * 4
            buffer[target:target + cell * 4] = pixels[source:source + cell * 4]
        print(f"  [{index + 1}/{len(paths)}] {os.path.basename(path)}", file=sys.stderr)

    sheet = bpy.data.images.new("contact_sheet", width=width, height=height, alpha=True)
    sheet.pixels = buffer
    sheet.filepath_raw = output_path
    sheet.file_format = "PNG"
    sheet.save()
    return width, height


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("png_dir")
    parser.add_argument("output")
    parser.add_argument("--columns", type=int, default=10)
    parser.add_argument("--cell", type=int, default=160,
                        help="size of each tile in pixels (default 160)")
    parser.add_argument("--pattern", default="*.png",
                        help="only tile files matching this glob")
    args = parser.parse_args()

    paths = sorted(os.path.join(args.png_dir, name)
                   for name in os.listdir(args.png_dir)
                   if fnmatch.fnmatch(name, args.pattern))
    if not paths:
        print(f"no files matching {args.pattern!r} in {args.png_dir}", file=sys.stderr)
        return 1

    width, height = build_sheet(paths, os.path.abspath(args.output), args.columns, args.cell)
    print(f"wrote {args.output} ({width}x{height}, {len(paths)} tiles)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
