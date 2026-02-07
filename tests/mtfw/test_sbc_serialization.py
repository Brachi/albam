
def test_export_header(sbc_imported, sbc_exported):
    sheader = sbc_imported.header
    dheader = sbc_exported.header
    assert sheader.magic == dheader.magic
