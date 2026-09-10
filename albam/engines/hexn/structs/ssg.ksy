meta:
  id: hexane_ssg
  endian: le
  title: Hexane Engine Archive format
  file-extension: ssg
  license: CC0-1.0
  ks-version: '0.11'

doc: |
  Two little-endian layouts share this header and file table, told apart by
  `id_magic`, and they differ only in how an entry's bytes are found inside
  `buffer_chunks`:

  * 6 packs every entry end to end in file-table order, each padded up to
    `size_padding`. `file_info.ofs_in_buffer_chunks` is not usable for that
    walk when the archive is chunk-compressed - see its own doc.
  * 5 leaves `size_padding` 0 and is never chunk-compressed
    (`size_chunks_info` is 0 in all 135 on a full install), so
    `file_info.ofs_in_buffer_chunks` addresses the stored buffer and the
    data itself alike, and is what locates an entry. Walking these end to
    end the way 6 is walked lands on another entry's bytes rather than
    failing - the offsets are real gaps, not padding this header describes.

  Verified on all 135 id_magic 5 archives of a full install (881 entries):
  read at `ofs_in_buffer_chunks`, every entry whose `file_type` names a
  format with a magic of its own starts on that magic exactly - "FM6S"
  (108/108 MODL), "MAT\\x07" (148/148 MATB), "DDS " (244/244 TPKD and
  244/244 TPKH), Havok's 57 e0 e0 57 (71/71 HAVK) - with no entry running
  past the end of the buffer and no two entries overlapping.

  `file_type` is a fourcc stored as a little-endian word, so the readable
  tag is its big-endian view. Two content families carry id_magic 5, and
  no archive mixes them: 130 weapon archives holding MODL/MATB/TPKD/TPKH/
  HAVK, and 5 under NIS/ holding cutscene/mocap streams (STMH/MCPH/SANM/
  SCAM/LAYO) instead - see albam.engines.hexn.fs, which mounts the former
  and refuses the latter. A TPKH entry is a 4-byte stub holding just the
  "DDS " magic; the real texture is the TPKD entry filed under the same
  name, which is the later of the two in every archive of either magic.

seq:
  - id: id_magic
    type: u4
    valid:
      any-of: [5, 6]
    doc: Layout version - see meta.doc for what the two differ in.
  - {id: reserved_01, type: u4}
  - {id: size_files_info, type: u4}
  - {id: size_file_names, type: u4}
  - {id: size_chunks_buffer, type: u4}
  - {id: reserverd_01, type: u4}
  - {id: size_chunks_info, type: u4}
  - {id: size_padding, type: u4}
  - {id: files_info, type: file_info, repeat: expr, repeat-expr: size_files_info / 32}
  - {id: chunk_sizes, type: u4, repeat: expr, repeat-expr: size_chunks_info / 4}
  - {id: file_names, size: size_file_names}

instances:
  buffer_chunks:
    pos: 32 + size_files_info + size_chunks_info + size_file_names
    size: size_chunks_buffer

types:
  file_info:
    seq:
      - {id: ident, type: u4}
      - {id: name_offset_rel, type: u4}
      - {id: size, type: u4}
      - {id: reserved_01, type: u4}
      - id: ofs_in_buffer_chunks
        type: u4
        doc: >
          Byte offset of this entry's data within `buffer_chunks` *as
          stored*, i.e. before decompression. An uncompressed archive
          (`size_chunks_info` == 0) stores the buffer verbatim, so this is
          equally the entry's offset in the data - that is what an
          id_magic 5 archive, always uncompressed, is read by. A
          compressed one instead puts the start of the zlib chunk holding
          the entry here, always exactly on a chunk boundary (confirmed
          against the cumulative `chunk_sizes` of a compressed id_magic 6
          archive), so it does not locate the entry in the decompressed
          stream and the end-to-end walk is what does.
      - {id: file_type, type: s4}
      - {id: unk_01, type: u4}
      - {id: unk_02, type: u4}
    instances: # convenience, although it's already read
      name:
        {type: str, terminator: 0, encoding: ASCII, pos: 32 + _parent.size_files_info + _parent.size_chunks_info + name_offset_rel}
