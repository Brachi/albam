meta:
  id: hexane_ssg
  endian: le
  title: Hexane Engine Archive format
  file-extension: ssg
  license: CC0-1.0
  ks-version: '0.11'

doc: |
  Two little-endian layouts, told apart by `id_magic`, share this header and
  file table and differ only in where an entry's bytes are in `buffer_chunks`:

  * 6 packs entries end to end in file-table order, each padded to
    `size_padding`.
  * 5 is never chunk-compressed and locates each entry at
    `file_info.ofs_in_buffer_chunks`; there are gaps between entries.

  `file_type` is a fourcc stored as a little-endian word. A TPKH entry is a
  4-byte stub holding just the "DDS " magic; the real texture is the TPKD
  entry filed under the same name.

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
