# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Xfs(ReadWriteKaitaiStruct):
    """Self-describing container holding a tree of objects whose classes are
    declared up front: a table of class definitions, each a type hash and a list
    of named, typed properties, followed by the values themselves.
    
    Not a format of its own so much as the serialization every property-driven
    resource uses - the same header carries stage layout (.lot), scene (.sce),
    state machines (.fsm) and a dozen others, distinguished by the minor version
    and by which classes they declare. Modelled against a verified dataset
    spanning fourteen extensions: major version 6 throughout, minor 1 to 14.
    
    Every offset in the file is relative to the end of the fixed header, i.e. to
    absolute offset 16, never to the start of the file.
    """

    class PropertyType(IntEnum):
        class_ = 1
        class_ref = 2
        bool_ = 3
        u8 = 4
        u16 = 5
        u32 = 6
        s8 = 8
        s16 = 9
        s32 = 10
        f32 = 12
        string = 14
        color = 15
        point = 16
        rect = 18
        matrix44 = 19
        vector3 = 20
        vector4 = 21
        quaternion = 22
        unk_36 = 36
        aabb = 47
        unk_54 = 54
        unk_55 = 55
        unk_57 = 57
        resource = 58
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Xfs, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.header = Xfs.XfsHeader(self._io, self, self._root)
        self.header._read()
        self.class_def_offsets = []
        for i in range(self.header.num_class_defs):
            self.class_def_offsets.append(self._io.read_u4le())

        self.class_defs = []
        for i in range(self.header.num_class_defs):
            _t_class_defs = Xfs.ClassDef(self._io, self, self._root)
            try:
                _t_class_defs._read()
            finally:
                self.class_defs.append(_t_class_defs)

        self.name_table = self._io.read_bytes((self._root.header.offset_data + 16) - self._io.pos())
        self.data = Xfs.DataSection(self._io, self, self._root)
        self.data._read()
        self._dirty = False


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        for i in range(len(self.class_def_offsets)):
            pass

        for i in range(len(self.class_defs)):
            pass
            self.class_defs[i]._fetch_instances()

        self.data._fetch_instances()


    def _write__seq(self, io=None):
        super(Xfs, self)._write__seq(io)
        self.header._write__seq(self._io)
        for i in range(len(self.class_def_offsets)):
            pass
            self._io.write_u4le(self.class_def_offsets[i])

        for i in range(len(self.class_defs)):
            pass
            self.class_defs[i]._write__seq(self._io)

        if len(self.name_table) != (self._root.header.offset_data + 16) - self._io.pos():
            raise kaitaistruct.ConsistencyError(u"name_table", (self._root.header.offset_data + 16) - self._io.pos(), len(self.name_table))
        self._io.write_bytes(self.name_table)
        self.data._write__seq(self._io)


    def _check(self):
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self._root, self.header._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self, self.header._parent)
        if len(self.class_def_offsets) != self.header.num_class_defs:
            raise kaitaistruct.ConsistencyError(u"class_def_offsets", self.header.num_class_defs, len(self.class_def_offsets))
        for i in range(len(self.class_def_offsets)):
            pass

        if len(self.class_defs) != self.header.num_class_defs:
            raise kaitaistruct.ConsistencyError(u"class_defs", self.header.num_class_defs, len(self.class_defs))
        for i in range(len(self.class_defs)):
            pass
            if self.class_defs[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"class_defs", self._root, self.class_defs[i]._root)
            if self.class_defs[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"class_defs", self, self.class_defs[i]._parent)

        if self.data._root != self._root:
            raise kaitaistruct.ConsistencyError(u"data", self._root, self.data._root)
        if self.data._parent != self:
            raise kaitaistruct.ConsistencyError(u"data", self, self.data._parent)
        self._dirty = False

    class ClassDef(ReadWriteKaitaiStruct):
        """Class definitions are stored back to back in the order class_def_offsets
        lists them, each exactly 8 + 24 * num_properties bytes, so the offsets
        are redundant with walking them in sequence - checked to agree on every
        file modelled.
        
        type_hash is a hash of the class's own name: CRC32 with its final
        complement undone and the top bit cleared, which is
        `(~crc32(name)) & 0x7FFFFFFF`. That makes a name recoverable wherever
        one can be found to hash - see xfs_classes.py, which carries the ones
        confirmed so far. Confirmed against every layout that stores the name of
        the class it points at beside the class itself, with no disagreements.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Xfs.ClassDef, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.type_hash = self._io.read_u4le()
            self.num_properties = self._io.read_u4le()
            self.properties = []
            for i in range(self.num_properties):
                _t_properties = Xfs.PropertyDef(self._io, self, self._root)
                try:
                    _t_properties._read()
                finally:
                    self.properties.append(_t_properties)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.properties)):
                pass
                self.properties[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xfs.ClassDef, self)._write__seq(io)
            self._io.write_u4le(self.type_hash)
            self._io.write_u4le(self.num_properties)
            for i in range(len(self.properties)):
                pass
                self.properties[i]._write__seq(self._io)



        def _check(self):
            if len(self.properties) != self.num_properties:
                raise kaitaistruct.ConsistencyError(u"properties", self.num_properties, len(self.properties))
            for i in range(len(self.properties)):
                pass
                if self.properties[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"properties", self._root, self.properties[i]._root)
                if self.properties[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"properties", self, self.properties[i]._parent)

            self._dirty = False


    class DataSection(ReadWriteKaitaiStruct):
        """size_ counts itself, so what follows is size_ - 4 bytes and runs to the
        end of the file. num_roots is 1 in every file modelled.
        
        The root is an instance of the first class declared, written straight
        out with no header of its own - only nested objects carry one.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Xfs.DataSection, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.num_roots = self._io.read_u4le()
            self.size_ = self._io.read_u4le()
            self.root = Xfs.ObjectBody(0, self._io, self, self._root)
            self.root._read()
            self._dirty = False


        def _fetch_instances(self):
            pass
            self.root._fetch_instances()


        def _write__seq(self, io=None):
            super(Xfs.DataSection, self)._write__seq(io)
            self._io.write_u4le(self.num_roots)
            self._io.write_u4le(self.size_)
            self.root._write__seq(self._io)


        def _check(self):
            if self.root._root != self._root:
                raise kaitaistruct.ConsistencyError(u"root", self._root, self.root._root)
            if self.root._parent != self:
                raise kaitaistruct.ConsistencyError(u"root", self, self.root._parent)
            if self.root.class_index != 0:
                raise kaitaistruct.ConsistencyError(u"root", 0, self.root.class_index)
            self._dirty = False


    class ObjectBody(ReadWriteKaitaiStruct):
        """An object is just its class's properties in declaration order. Nothing
        is aligned and nothing is padded, so a position inside the value stream
        only means something to a reader that has walked everything before it.
        """
        def __init__(self, class_index, _io=None, _parent=None, _root=None):
            super(Xfs.ObjectBody, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.class_index = class_index

        def _read(self):
            self.properties = []
            for i in range(self._root.class_defs[self.class_index].num_properties):
                _t_properties = Xfs.PropertyValues(self.class_index, i, self._io, self, self._root)
                try:
                    _t_properties._read()
                finally:
                    self.properties.append(_t_properties)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.properties)):
                pass
                self.properties[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xfs.ObjectBody, self)._write__seq(io)
            for i in range(len(self.properties)):
                pass
                self.properties[i]._write__seq(self._io)



        def _check(self):
            if len(self.properties) != self._root.class_defs[self.class_index].num_properties:
                raise kaitaistruct.ConsistencyError(u"properties", self._root.class_defs[self.class_index].num_properties, len(self.properties))
            for i in range(len(self.properties)):
                pass
                if self.properties[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"properties", self._root, self.properties[i]._root)
                if self.properties[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"properties", self, self.properties[i]._parent)
                if self.properties[i].class_index != self.class_index:
                    raise kaitaistruct.ConsistencyError(u"properties", self.class_index, self.properties[i].class_index)
                if self.properties[i].prop_index != i:
                    raise kaitaistruct.ConsistencyError(u"properties", i, self.properties[i].prop_index)

            self._dirty = False


    class ObjectRef(ReadWriteKaitaiStruct):
        """A reference points at nothing, carries an object inline, or names one
        already written; tag says which, and only the inline form has a body.
        
        tag is 0xfffe for a null reference. An odd tag carries an object inline
        and encodes its class as 2 * class_index + 1. An even tag is a
        back-reference to an object emitted earlier - `index` identifies it and
        nothing follows - which is how one object points at another without the
        tree having to nest, as a sprite does at its parent.
        
        index counts objects as they are written, from one, and is present in
        every form; it is unused for a null reference. size_ counts itself, as
        it does in the data section.
        
        Every back-reference in the modelled data carries tag 4, so the class
        encoding for the even form is consistent with tag / 2 but rests on that
        one value.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Xfs.ObjectRef, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.tag = self._io.read_u2le()
            self.index = self._io.read_u2le()
            if self.is_inline:
                pass
                self.size_ = self._io.read_u4le()

            if self.is_inline:
                pass
                self._raw_body = self._io.read_bytes(self.size_ - 4)
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = Xfs.ObjectBody(self.class_index, _io__raw_body, self, self._root)
                self.body._read()

            self._dirty = False


        def _fetch_instances(self):
            pass
            if self.is_inline:
                pass

            if self.is_inline:
                pass
                self.body._fetch_instances()



        def _write__seq(self, io=None):
            super(Xfs.ObjectRef, self)._write__seq(io)
            self._io.write_u2le(self.tag)
            self._io.write_u2le(self.index)
            if self.is_inline:
                pass
                self._io.write_u4le(self.size_)

            if self.is_inline:
                pass
                _io__raw_body = KaitaiStream(BytesIO(bytearray(self.size_ - 4)))
                self._io.add_child_stream(_io__raw_body)
                _pos2 = self._io.pos()
                self._io.seek(self._io.pos() + (self.size_ - 4))
                def handler(parent, _io__raw_body=_io__raw_body):
                    self._raw_body = _io__raw_body.to_byte_array()
                    if len(self._raw_body) != self.size_ - 4:
                        raise kaitaistruct.ConsistencyError(u"raw(body)", self.size_ - 4, len(self._raw_body))
                    parent.write_bytes(self._raw_body)
                _io__raw_body.write_back_handler = KaitaiStream.WriteBackHandler(_pos2, handler)
                self.body._write__seq(_io__raw_body)



        def _check(self):
            if self.is_inline:
                pass

            if self.is_inline:
                pass
                if self.body._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"body", self._root, self.body._root)
                if self.body._parent != self:
                    raise kaitaistruct.ConsistencyError(u"body", self, self.body._parent)
                if self.body.class_index != self.class_index:
                    raise kaitaistruct.ConsistencyError(u"body", self.class_index, self.body.class_index)

            self._dirty = False

        @property
        def class_index(self):
            if hasattr(self, '_m_class_index'):
                return self._m_class_index

            self._m_class_index = ((self.tag - 1) // 2 if self.is_inline else self.tag // 2)
            return getattr(self, '_m_class_index', None)

        def _invalidate_class_index(self):
            del self._m_class_index
        @property
        def is_inline(self):
            if hasattr(self, '_m_is_inline'):
                return self._m_is_inline

            self._m_is_inline =  (((not (self.is_null))) and (self.tag % 2 == 1)) 
            return getattr(self, '_m_is_inline', None)

        def _invalidate_is_inline(self):
            del self._m_is_inline
        @property
        def is_null(self):
            if hasattr(self, '_m_is_null'):
                return self._m_is_null

            self._m_is_null = self.tag >= 65534
            return getattr(self, '_m_is_null', None)

        def _invalidate_is_null(self):
            del self._m_is_null

    class PropertyDef(ReadWriteKaitaiStruct):
        """size is the property's width in the value stream for every type that has
        a fixed one: 1 for bool_ and the 8-bit integers, 2 for the 16-bit ones,
        4 for the 32-bit types and for colour and the two class types, 8 for
        point, unk_54 and unk_55, 16 for rect, vector3, vector4, quaternion and
        unk_36, 32 for aabb, and 64 for matrix44 and unk_57.
        
        string and resource also declare 4, the width a loaded property needs
        for the pointer it ends up holding, but neither occupies four bytes in
        the file: both are written inline and are as long as their text. A
        reader that trusts size for those two desynchronises the value stream
        from that point on.
        
        reserved is 16 zero bytes in every file seen, the room a loaded property
        needs for pointers the file itself has no use for.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Xfs.PropertyDef, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__enabled = True

        def _read(self):
            self.name_offset = self._io.read_u4le()
            self.type = KaitaiStream.resolve_enum(Xfs.PropertyType, self._io.read_u1())
            self.flags = self._io.read_u1()
            self.size = self._io.read_u2le()
            self.reserved = self._io.read_bytes(16)
            self._dirty = False


        def _fetch_instances(self):
            pass
            _ = self.name
            if hasattr(self, '_m_name'):
                pass



        def _write__seq(self, io=None):
            super(Xfs.PropertyDef, self)._write__seq(io)
            self._should_write_name = self.name__enabled
            self._io.write_u4le(self.name_offset)
            self._io.write_u1(int(self.type))
            self._io.write_u1(self.flags)
            self._io.write_u2le(self.size)
            self._io.write_bytes(self.reserved)


        def _check(self):
            if len(self.reserved) != 16:
                raise kaitaistruct.ConsistencyError(u"reserved", 16, len(self.reserved))
            if self.name__enabled:
                pass
                if KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0) != -1:
                    raise kaitaistruct.ConsistencyError(u"name", -1, KaitaiStream.byte_array_index_of((self._m_name).encode(u"ASCII"), 0))

            self._dirty = False

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            if not self.name__enabled:
                return None

            io = self._root._io
            _pos = io.pos()
            io.seek(16 + self.name_offset)
            self._m_name = (io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._dirty = True
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            io = self._root._io
            _pos = io.pos()
            io.seek(16 + self.name_offset)
            io.write_bytes((self._m_name).encode(u"ASCII"))
            io.write_u1(0)
            io.seek(_pos)


    class PropertyValues(ReadWriteKaitaiStruct):
        """Every property is a count followed by that many values, one for a plain
        scalar and zero for an empty array or an unset reference. Types the
        property carries a width for are taken at that width, whatever they
        mean; string and resource are written where they stand and ignore it.
        """
        def __init__(self, class_index, prop_index, _io=None, _parent=None, _root=None):
            super(Xfs.PropertyValues, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.class_index = class_index
            self.prop_index = prop_index

        def _read(self):
            self.num_values = self._io.read_u4le()
            self.values = []
            for i in range(self.num_values):
                _on = self.property.type
                if _on == Xfs.PropertyType.class_:
                    pass
                    _t_values = Xfs.ObjectRef(self._io, self, self._root)
                    try:
                        _t_values._read()
                    finally:
                        self.values.append(_t_values)
                elif _on == Xfs.PropertyType.class_ref:
                    pass
                    _t_values = Xfs.ObjectRef(self._io, self, self._root)
                    try:
                        _t_values._read()
                    finally:
                        self.values.append(_t_values)
                elif _on == Xfs.PropertyType.resource:
                    pass
                    _t_values = Xfs.ResourceValue(self._io, self, self._root)
                    try:
                        _t_values._read()
                    finally:
                        self.values.append(_t_values)
                elif _on == Xfs.PropertyType.string:
                    pass
                    _t_values = Xfs.StringValue(self._io, self, self._root)
                    try:
                        _t_values._read()
                    finally:
                        self.values.append(_t_values)
                else:
                    pass
                    _t_values = Xfs.RawValue(self.property.size, self._io, self, self._root)
                    try:
                        _t_values._read()
                    finally:
                        self.values.append(_t_values)

            self._dirty = False


        def _fetch_instances(self):
            pass
            for i in range(len(self.values)):
                pass
                _on = self.property.type
                if _on == Xfs.PropertyType.class_:
                    pass
                    self.values[i]._fetch_instances()
                elif _on == Xfs.PropertyType.class_ref:
                    pass
                    self.values[i]._fetch_instances()
                elif _on == Xfs.PropertyType.resource:
                    pass
                    self.values[i]._fetch_instances()
                elif _on == Xfs.PropertyType.string:
                    pass
                    self.values[i]._fetch_instances()
                else:
                    pass
                    self.values[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xfs.PropertyValues, self)._write__seq(io)
            self._io.write_u4le(self.num_values)
            for i in range(len(self.values)):
                pass
                _on = self.property.type
                if _on == Xfs.PropertyType.class_:
                    pass
                    self.values[i]._write__seq(self._io)
                elif _on == Xfs.PropertyType.class_ref:
                    pass
                    self.values[i]._write__seq(self._io)
                elif _on == Xfs.PropertyType.resource:
                    pass
                    self.values[i]._write__seq(self._io)
                elif _on == Xfs.PropertyType.string:
                    pass
                    self.values[i]._write__seq(self._io)
                else:
                    pass
                    self.values[i]._write__seq(self._io)



        def _check(self):
            if len(self.values) != self.num_values:
                raise kaitaistruct.ConsistencyError(u"values", self.num_values, len(self.values))
            for i in range(len(self.values)):
                pass
                _on = self.property.type
                if _on == Xfs.PropertyType.class_:
                    pass
                    if self.values[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"values", self._root, self.values[i]._root)
                    if self.values[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"values", self, self.values[i]._parent)
                elif _on == Xfs.PropertyType.class_ref:
                    pass
                    if self.values[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"values", self._root, self.values[i]._root)
                    if self.values[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"values", self, self.values[i]._parent)
                elif _on == Xfs.PropertyType.resource:
                    pass
                    if self.values[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"values", self._root, self.values[i]._root)
                    if self.values[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"values", self, self.values[i]._parent)
                elif _on == Xfs.PropertyType.string:
                    pass
                    if self.values[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"values", self._root, self.values[i]._root)
                    if self.values[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"values", self, self.values[i]._parent)
                else:
                    pass
                    if self.values[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"values", self._root, self.values[i]._root)
                    if self.values[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"values", self, self.values[i]._parent)
                    if self.values[i].len_value != self.property.size:
                        raise kaitaistruct.ConsistencyError(u"values", self.property.size, self.values[i].len_value)

            self._dirty = False

        @property
        def property(self):
            if hasattr(self, '_m_property'):
                return self._m_property

            self._m_property = self._root.class_defs[self.class_index].properties[self.prop_index]
            return getattr(self, '_m_property', None)

        def _invalidate_property(self):
            del self._m_property

    class RawValue(ReadWriteKaitaiStruct):
        def __init__(self, len_value, _io=None, _parent=None, _root=None):
            super(Xfs.RawValue, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self.len_value = len_value

        def _read(self):
            self.value = self._io.read_bytes(self.len_value)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xfs.RawValue, self)._write__seq(io)
            self._io.write_bytes(self.value)


        def _check(self):
            if len(self.value) != self.len_value:
                raise kaitaistruct.ConsistencyError(u"value", self.len_value, len(self.value))
            self._dirty = False


    class ResourceValue(ReadWriteKaitaiStruct):
        """A reference to another resource, named rather than numbered: the class
        that will load it and the path it lives at, both inline and both
        terminated. The path carries no extension - the class supplies it.
        
        An unset reference is still written out in full, with the literal class
        name `null` and an empty path, so a resource property is present whether
        or not it points anywhere - roughly half of those in the modelled data
        are null. kind is 2 in every value seen, null ones included.
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Xfs.ResourceValue, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.kind = self._io.read_u1()
            self.class_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self.path = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xfs.ResourceValue, self)._write__seq(io)
            self._io.write_u1(self.kind)
            self._io.write_bytes((self.class_name).encode(u"ASCII"))
            self._io.write_u1(0)
            self._io.write_bytes((self.path).encode(u"ASCII"))
            self._io.write_u1(0)


        def _check(self):
            if KaitaiStream.byte_array_index_of((self.class_name).encode(u"ASCII"), 0) != -1:
                raise kaitaistruct.ConsistencyError(u"class_name", -1, KaitaiStream.byte_array_index_of((self.class_name).encode(u"ASCII"), 0))
            if KaitaiStream.byte_array_index_of((self.path).encode(u"ASCII"), 0) != -1:
                raise kaitaistruct.ConsistencyError(u"path", -1, KaitaiStream.byte_array_index_of((self.path).encode(u"ASCII"), 0))
            self._dirty = False


    class StringValue(ReadWriteKaitaiStruct):
        """Written into the value stream where it stands, not into a table."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Xfs.StringValue, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.value = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xfs.StringValue, self)._write__seq(io)
            self._io.write_bytes((self.value).encode(u"ASCII"))
            self._io.write_u1(0)


        def _check(self):
            if KaitaiStream.byte_array_index_of((self.value).encode(u"ASCII"), 0) != -1:
                raise kaitaistruct.ConsistencyError(u"value", -1, KaitaiStream.byte_array_index_of((self.value).encode(u"ASCII"), 0))
            self._dirty = False


    class XfsHeader(ReadWriteKaitaiStruct):
        """version_major is 6 everywhere seen; version_minor identifies the schema
        the declared classes belong to and tracks the extension rather than the
        container (.fsm is 6.1, .lot 6.4, .sce 6.11, .lnk 6.14).
        """
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Xfs.XfsHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.ident = self._io.read_bytes(4)
            if not self.ident == b"\x58\x46\x53\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x58\x46\x53\x00", self.ident, self._io, u"/types/xfs_header/seq/0")
            self.version_major = self._io.read_u2le()
            self.version_minor = self._io.read_u2le()
            self.num_class_defs = self._io.read_u4le()
            self.offset_data = self._io.read_u4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xfs.XfsHeader, self)._write__seq(io)
            self._io.write_bytes(self.ident)
            self._io.write_u2le(self.version_major)
            self._io.write_u2le(self.version_minor)
            self._io.write_u4le(self.num_class_defs)
            self._io.write_u4le(self.offset_data)


        def _check(self):
            if len(self.ident) != 4:
                raise kaitaistruct.ConsistencyError(u"ident", 4, len(self.ident))
            if not self.ident == b"\x58\x46\x53\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x58\x46\x53\x00", self.ident, None, u"/types/xfs_header/seq/0")
            self._dirty = False



