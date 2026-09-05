import io
import os
import struct
import zlib

import bpy
from bc7enc import unpack_dds

from ...lib.dds import DDSHeader

_FOURCC_TO_DDS_FORMAT = {
    b"DXT1": "DXT1",
    b"DXT5": "DXT5",
}

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _texture_suffix(texture_path):
    stem = os.path.basename(texture_path).rsplit(".", 1)[0]
    return stem[-2:].lower()


def _dds_format(dds_header):
    dds_format = _FOURCC_TO_DDS_FORMAT.get(dds_header.pixelfmt_dwFourCC)
    if dds_format is None:
        raise ValueError(f"Unsupported DDS FourCC: {dds_header.pixelfmt_dwFourCC!r}")
    return dds_format


def _png_chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))


def _encode_png(width, height, rgba_bytes):
    """Minimal 8-bit RGBA PNG encoder - stdlib zlib/struct only, no new
    dependency. Lets a decoded-in-Python image (here, bc7enc's unswizzled
    normal map bytes) go through the same pack(data=..., data_len=...) +
    source="FILE" path already used for _d/_s/_g's raw DDS bytes below,
    instead of the far slower bpy.types.Image.pixels (a per-float Python
    assignment - measured much slower for 2048x2048+ textures, since it
    round-trips millions of individual Python float objects). Letting
    Blender's own PNG loader do the decode also means it applies the same
    row-order handling it already does for DDS, so the scanlines here stay
    in their natural top-to-bottom order - no manual row-flip needed.

    One filter-type byte (0 = "None") per scanline, per the PNG spec; a
    single zlib-compressed IDAT (level 1 - this is a transient in-memory
    blob Blender immediately decodes again, not a file to store, so
    compression ratio doesn't matter, only encode speed).
    """
    row_stride = width * 4
    raw = bytearray((row_stride + 1) * height)
    for y in range(height):
        src = y * row_stride
        dst = y * (row_stride + 1) + 1
        raw[dst:dst + row_stride] = rgba_bytes[src:src + row_stride]

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # bit depth 8, color type 6 = RGBA
    idat = zlib.compress(bytes(raw), 1)
    return _PNG_SIGNATURE + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", idat) + _png_chunk(b"IEND", b"")


def _build_unswizzled_normal_image(display_name, texture_bytes, dds_header):
    """_n maps are DXT5 with the classic "agnm"/DXT5nm swizzle (aka "green
    cast"): the real X component lives in Alpha (moved there for its higher
    per-block precision) and Z isn't stored at all, only reconstructable as
    sqrt(1 - x^2 - y^2) - confirmed against real hunk/partygirl textures:
    raw DXT5 R/B are near-constant filler (~0.14, not real per-texel data),
    while Alpha and Green carry real, independent variation, and treating
    (Alpha, Green) as (X, Y) satisfies x^2+y^2<=1 for ~100% of sampled
    texels (a precondition for a valid Z reconstruction).

    bc7enc's unswizzle_agnm (native, see its DDS_FORMATS_BLOCK_SIZE/SWIZZLES
    tables) does exactly this unswizzle + reconstruction - verified: R
    becomes the old Alpha, G is passed through unchanged, B goes from a flat
    ~0.14 to a proper reconstructed ~1.0 mean (surfaces mostly facing the
    viewer, as expected for real Z), and treating the resulting RGB as a
    standard tangent-space normal (2*c-1 per channel) yields unit-length
    vectors (mean ~1.0000, stdev ~0.002 - measured, not assumed).

    Green's sign isn't touched by unswizzle_agnm and stays whatever the
    source DDS authored; material.py's ShaderNodeNormalMap is set to
    convention="DIRECTX" to account for that.
    """
    width, height = dds_header.dwWidth, dds_header.dwHeight
    dds_format = _dds_format(dds_header)
    data_offset = 4 + dds_header.dwSize  # magic + header, no DX10 extension for DXT1/DXT5
    pixel_bytes = unpack_dds(io.BytesIO(texture_bytes), width, height, dds_format, data_offset,
                             unswizzle="agnm")
    png_bytes = _encode_png(width, height, bytes(pixel_bytes))

    bl_image = bpy.data.images.new(display_name, width, height, alpha=True)
    bl_image.source = "FILE"
    bl_image.pack(data=png_bytes, data_len=len(png_bytes))
    return bl_image


def build_blender_textures(texture_paths, context, root_id=None):
    vfs = context.scene.albam.vfs
    tex_mapping = {}
    for path in texture_paths:
        # Unreachable textures are skipped, not fatal - see
        # material.build_blender_materials for when that happens. root_id
        # prefers the model's own mounted root - see vfs.get_vfile.
        try:
            texture_vfile = vfs.get_vfile("reorc", path, root_id=root_id)
        except KeyError:
            print(f"[{path}] texture not found, skipping")
            continue
        texture_bytes = texture_vfile.get_bytes()
        dds_header = DDSHeader()
        io.BytesIO(texture_bytes).readinto(dds_header)

        if _texture_suffix(path) == "_n":
            bl_image = _build_unswizzled_normal_image(os.path.basename(path), texture_bytes, dds_header)
        else:
            bl_image = bpy.data.images.new(os.path.basename(path), dds_header.dwWidth, dds_header.dwHeight)
            bl_image.source = "FILE"
            bl_image.pack(data=bytes(texture_bytes), data_len=len(texture_bytes))

        tex_mapping[path] = bl_image

    return tex_mapping
