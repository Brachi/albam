
def test_export_header(lmt_imported, lmt_exported):
    slmt = lmt_imported
    dlmt = lmt_exported
    slmt.id_magic == dlmt.id_magic
    slmt.version == dlmt.version
    slmt.num_block_offsets == dlmt.num_block_offsets
