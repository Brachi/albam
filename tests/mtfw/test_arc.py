from albam.engines.mtfw.archive import ArcWrapper


def test_arc(arc_file):

    arc = ArcWrapper(arc_file["filepath"])
    assert arc.parsed.header.num_files < 410