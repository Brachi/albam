"""Decode an XMemCompress stream with somebody else's LZX decoder.

Round-tripping a stream through albam's own decoder says the encoder and the
decoder agree; it says nothing about whether the game would take the stream,
because that decoder is the more forgiving of the two - the .lfs encoder
shipped three bugs it read back perfectly and the game rejected. Loading an
archive in the game is the only real answer, and it is not something a test
can do. This is the next thing down: a decoder written by someone else, from
the format rather than from albam.

An XMemCompress stream is LZX with a 0x20000 window, framed by inline
headers. Microsoft's CAB carries the same bitstream with the same 32768-byte
framing, only with each frame's two sizes moved out into a CFDATA record, and
LZX with a 0x20000 window is what a CAB folder of compression type LZX:17
holds. So the frames can be lifted out of one framing and dropped into the
other without touching a bit of the LZX itself, and then p7zip - whose LZX
decoder shares no code and no lineage with albam's - reads them.

That the transplant is faithful is not assumed: test_a_shipped_stream_decodes
in tests/mtfw/test_arc_compression.py runs shipped Devil May Cry 4 entries
through it and requires the same bytes the game's own archives decode to.

p7zip is not a dependency of anything here; callers skip when it is missing.
"""
import os
import shutil
import struct
import subprocess
import tempfile

from tests.xcompress_frames import frames_of

CAB_NAME = "entry.bin"
# CFFOLDER.typeCompress: LZX in the low byte, the window's log2 above it.
CAB_LZX = 0x0003
XMEM_WINDOW_BITS = 17


def sevenzip():
    """The 7z binary, or None if p7zip is not installed."""
    return shutil.which("7z") or shutil.which("7za")


def build_cab(frames, size):
    """`frames` as a one-file, one-folder CAB whose folder is LZX:17.

    The three tables a CAB opens with are fixed-shape records (see the CAB
    format's CFHEADER/CFFOLDER/CFFILE); the frames go in behind them as one
    CFDATA each, whose checksum field is left at zero - the format's own way
    of saying there is no checksum.
    """
    cfdata = bytearray()
    for _header, uncompressed, data in frames:
        cfdata += struct.pack("<IHH", 0, len(data), uncompressed) + data
    cffile = struct.pack("<IIHHHH", size, 0, 0, 0x2A21, 0, 0x20) + CAB_NAME.encode() + b"\0"
    header_size, folder_size = 36, 8
    files_offset = header_size + folder_size
    data_offset = files_offset + len(cffile)
    cffolder = struct.pack("<IHH", data_offset, len(frames),
                           CAB_LZX | (XMEM_WINDOW_BITS << 8))
    cfheader = b"MSCF" + struct.pack(
        "<IIIIIBBHHHHH", 0, data_offset + len(cfdata), 0, files_offset, 0,
        3, 1, 1, 1, 0, 0, 0)
    assert len(cfheader) == header_size
    return bytes(cfheader + cffolder + cffile + cfdata)


def independent_decompress(stream, size):
    """`stream` decoded to `size` bytes by p7zip's LZX decoder."""
    binary = sevenzip()
    assert binary, "p7zip is not installed"
    cab = build_cab(frames_of(stream)[0], size)
    with tempfile.TemporaryDirectory() as directory:
        cab_path = os.path.join(directory, "stream.cab")
        with open(cab_path, "wb") as f:
            f.write(cab)
        result = subprocess.run([binary, "e", "-y", "-o" + directory, cab_path],
                                capture_output=True)
        decoded = os.path.join(directory, CAB_NAME)
        if not os.path.exists(decoded):
            raise RuntimeError(
                f"7z could not read the stream: {result.stdout.decode(errors='replace')[-500:]}")
        with open(decoded, "rb") as f:
            return f.read()
