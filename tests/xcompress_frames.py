"""Walking a bare XMemCompress stream's frames from the outside.

Deliberately not the encoder's own bookkeeping and not the decoder's loop:
this reads the stream the way something that has only the bytes has to,
which is what lets a test say the frames are shaped the way the game's own
are rather than the way albam meant them to be.

A frame starting with 0xFF carries both of its sizes in a five byte header;
any other frame carries only the compressed size, in two bytes, and means a
full 32768 bytes out.
"""
FRAME_SIZE = 32768
LONG_HEADER_MARKER = 0xFF
LONG_HEADER_SIZE = 5
SHORT_HEADER_SIZE = 2


def frames_of(stream):
    """`stream` as (header size, uncompressed size, compressed bytes) per
    frame, plus whatever follows the last one.

    Stops on a header declaring no compressed bytes, which is how a reader
    walking frames rather than counting output finds the end of an .lfs
    chunk; an .arc entry's stream simply runs out instead.
    """
    frames = []
    position = 0
    while position < len(stream):
        if stream[position] == LONG_HEADER_MARKER:
            header = LONG_HEADER_SIZE
            uncompressed = (stream[position + 1] << 8) | stream[position + 2]
            compressed = (stream[position + 3] << 8) | stream[position + 4]
        else:
            header = SHORT_HEADER_SIZE
            uncompressed = FRAME_SIZE
            compressed = (stream[position] << 8) | stream[position + 1]
        if compressed == 0:
            break
        position += header
        frames.append((header, uncompressed, stream[position:position + compressed]))
        position += compressed
    return frames, stream[position:]
