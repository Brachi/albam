from kaitaistruct import BytesIO, KaitaiStream, ReadWriteKaitaiStruct

# The only attributes that legitimately point at another ReadWriteKaitaiStruct
# without "belonging" to kaitai_obj - back-references to the enclosing
# object(s). Recursing into these would just walk back up the tree (and,
# for _root, potentially loop forever between a node and its root).
_BACKREFERENCE_KEYS = frozenset({"_parent", "_root"})


def check_recursive(kaitai_obj):
    """Calls ._check() on every ReadWriteKaitaiStruct reachable from
    kaitai_obj, children before kaitai_obj itself.

    A generated struct's own ._check() only validates its own direct
    fields (and, for a nested struct field, that its _root/_parent linkage
    is correct) - it never clears a nested struct's own _dirty flag. A
    freshly constructed/mutated nested struct (e.g. tex.cube_faces[i], or
    vertex_struct.position) stays dirty forever unless something calls
    ._check() on that specific object too, so ._write() on the outer
    object raises ConsistencyNotCheckedError as soon as it recurses into
    that still-dirty child - see kaitaistruct.ReadWriteKaitaiStruct.

    Deliberately not filtered by a leading underscore: a kaitai "instance"
    (lazily computed field with its own setter, e.g. Mrl.resources) stores
    its materialized value in a private `_m_<name>` attribute - skipping
    every underscore-prefixed key would silently skip those too.
    """
    for key, value in vars(kaitai_obj).items():
        if key in _BACKREFERENCE_KEYS:
            continue
        if isinstance(value, ReadWriteKaitaiStruct):
            check_recursive(value)
        elif isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, ReadWriteKaitaiStruct):
                    check_recursive(item)
    kaitai_obj._check()


def parse(kaitai_cls, data, *params):
    """Parses `data` with `kaitai_cls`, passing `params` to its constructor.

    kaitaistruct's own `from_bytes` hardcodes a parameterless constructor,
    so it can't be used with a struct that declares `params:` in its .ksy
    (every mtfw model/texture struct takes an `app_id`, since some fields
    differ per app rather than per format version).
    """
    obj = kaitai_cls(*params, KaitaiStream(BytesIO(data)))
    obj._read()
    return obj
