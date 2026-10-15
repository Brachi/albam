import io
import struct
import zlib
import xml.etree.ElementTree as ET
from ctypes import Structure, Union, c_uint32
from collections import defaultdict
from .mt_classes import DTI_HASHES, RV_DTI_HASHES, DTI_FILE_HASHES, RV_DTI_FILE_HASHES
from .mt_classes import MtPropertyType, RV_MtPropertyType
from ..engines.mtfw.structs import sdl_156, xfs  # pla
from . import mt_types as mt
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


SDL_TRACK_ENUM = {
    1: 'root_track',
    2: 'classref_track',  # unit track ?
    4: 'class_track',  # another root ?
    5: 'object_track',
    6: 'int_track',
    7: 'vector_track',
    8: 'float_track',
    9: 'bool_track',
    10: 'ref_track',
    11: 'resource_track',
    13: 'event_track'
}

RV_SDL_TRACK_ENUM = {v: k for k, v in SDL_TRACK_ENUM.items()}

PLA_TRACK_ENUM = {
    1: 'root_track',
    3: 'group_track',  # unit track ?
    4: 'unit_track',  # another root ?
    5: 'object_track',
    6: 'bool_track',
    7: 'int_track',
    8: 'float_track',
    9: 'vector_track',
    10: 'ref_track',
    11: 'resource_track',
}

RV_PLA_TRACK_ENUM = {v: k for k, v in PLA_TRACK_ENUM.items()}


def flatten_tree(node, node_list, p_index):
    if node.tag in RV_SDL_TRACK_ENUM:
        curr_index = len(node_list)
        node_list.append((node, p_index))
        if RV_SDL_TRACK_ENUM[node.tag] > 5:
            return
        else:
            for c in node:
                flatten_tree(c, node_list, curr_index)
    else:
        node_list.append((node, len(node_list)))
        for c in node:
            flatten_tree(c, node_list, 0)


def write_name(buf, names):
    name_dict = defaultdict()
    for name in names:
        name_dict[name] = buf.tell()
        buf.write(bytes(name, 'utf-8'))
        buf.write(b'\0')
    buf_size = buf.getbuffer().nbytes
    if buf_size % 4 != 0:
        buf.write(b'\0' * (4 - (buf_size % 4)))
    return name_dict


def pack_timeframe(node):
    frame_time = int(node.attrib['timermarker'])
    frame_type = int(node.attrib['marker_type'])

    class TimerFrame(Structure):
        _fields_ = (
            ('frame', c_uint32, 24),
            ('type', c_uint32, 8)
        )

    class TimerFrameUnion(Union):
        _fields_ = (
            ('timeframe', TimerFrame),
            ('raw', c_uint32)
        )
    frame = TimerFrame()
    frame.type = frame_type
    frame.frame = frame_time
    frame_union = TimerFrameUnion()
    frame_union.timeframe = frame
    return struct.pack('I', frame_union.raw)


def traverse_tree(node, dst_sdl, val_buffer, name_buffer, name_dict, p_index=0, offset=0):
    track = dst_sdl.Track(_parent=dst_sdl, _root=dst_sdl._root)
    track.type = RV_SDL_TRACK_ENUM[node.tag]
    track.prop_type = MtPropertyType[node.attrib['prop_type']]
    track.num_frames = len(node.findall('item'))
    track.parent = p_index
    track.name_ofs = name_dict[node.attrib['name']]
    track.dti_ref = 0
    track.timing_ref = offset
    track.data_ref = offset
    track.timing_frames__to_write = False
    track.data__to_write = False
    track.name__to_write = False

    if 'dti' in node.attrib:
        track.dti_ref = DTI_HASHES.get(node.attrib['dti'], int(node.attrib['dti'], 16))

    if RV_SDL_TRACK_ENUM[node.tag] > 5:
        if node.tag == 'int_track' or node.tag == 'bool_track':
            track.timing_ref += val_buffer.getbuffer().nbytes
            time_val = [pack_timeframe(x) for x in node.iter('item')]
            val_buffer.write(b''.join(bytes(x) for x in time_val))
            val_buffer.write(b'\0\0\0\0')
            track.data_ref += val_buffer.getbuffer().nbytes
            if node.attrib['prop_type'][5] == 'U':
                val_buffer.write(b''.join([struct.pack('I', int(x.attrib['value'])) for x in node.iter('item')]))
            else:
                val_buffer.write(b''.join([struct.pack('i', int(x.attrib['value'])) for x in node.iter('item')]))
            track.num_frames += len(time_val)

        elif node.tag == 'float_track':
            track.timing_ref += val_buffer.getbuffer().nbytes
            time_val = [pack_timeframe(x) for x in
                        node.iter('item')]
            val_buffer.write(b''.join(bytes(x) for x in time_val))
            val_buffer.write(b'\0\0\0\0')
            track.data_ref += val_buffer.getbuffer().nbytes
            val_buffer.write(b''.join([struct.pack('f', float(x.attrib['value'])) for x in node.iter('item')]))
            track.num_frames += len(time_val)

        elif node.tag == 'resource_track':
            track.timing_ref += val_buffer.getbuffer().nbytes
            time_val = [pack_timeframe(x) for x in
                        node.iter('item')]
            val_buffer.write(b''.join(bytes(x) for x in time_val))
            val_buffer.write(b'\0\0\0\0')
            items = list(node.iter('item'))
            track.data_ref += val_buffer.getbuffer().nbytes
            for i in range(len(time_val)):
                val_buffer.write(struct.pack('I', name_buffer.tell()))
                print(items[i].attrib['ref_dti'])
                dti_hash = DTI_HASHES.get(items[i].attrib['ref_dti'], int(items[i].attrib['ref_dti']))
                print(dti_hash)
                name_buffer.write(struct.pack('I', dti_hash))
                name_buffer.write(bytes(items[i].attrib['ref_path'], 'utf-8'))
                name_buffer.write(b'\0')
            track.num_frames += len(time_val)

        elif node.tag == 'vector_track':
            track.timing_ref += val_buffer.getbuffer().nbytes
            time_val = [pack_timeframe(x) for x in
                        node.iter('item')]
            val_buffer.write(b''.join(bytes(x) for x in time_val))
            val_buffer.write(b'\0\0\0\0')
            track.data_ref += val_buffer.getbuffer().nbytes
            track.num_frames += len(time_val)
            for it in node.iter('item'):
                for c in it:
                    val_buffer.write(struct.pack('f', float(c.text)))
    return track


def from_pla(pla_file):
    root = ET.Element('root')
    root.attrib['frames'] = str(pla_file.header.frames)
    sorted_tracks = pla_file.tracks.copy()
    sorted_tracks.sort(key=lambda x: x.parent)
    # parents = defaultdict(list)
    elements = []

    for i, track in enumerate(pla_file.tracks[1:]):
        # parents[track.parent].append(i)
        track_type = PLA_TRACK_ENUM[track.type]
        e = ET.Element(PLA_TRACK_ENUM[track.type],attrib={})
        e.attrib['prop_type'] = RV_MtPropertyType[track.prop_type]
        e.attrib['org_dti_ofs'] = hex(track.dti_ref)
        e.attrib['org_data_ofs'] = hex(track.data_ref)
        e.attrib['name'] = track.name
        if track.type == 2:
            e.attrib['dti'] = RV_DTI_HASHES[track.dti_ref]

        if track.type == 4:
            e.attrib['move_line'] = f'{track.move_line}'

        if track.num_frames > 0:
            data = ET.SubElement(e, 'data')
            for j in range(track.num_frames):
                value = ET.SubElement(data, 'item', attrib={
                    'timermarker':str(track.timing_frames[j].frame),
                    'marker_type':str(track.timing_frames[j].type)
                })
                if track.type in [6, 7, 8]:
                    value.attrib['value'] = str(track.data[j])
                if track.type == 9:
                    val = mt.type_to_class[track.prop_type]()
                    val.read(track.data[j])
                    for k in val.__annotations__:
                        it = ET.SubElement(value, k, attrib={})
                        it.text = str(getattr(val, k))
                if track.type == 0xB:
                    if track.data[j].ref_ofs:
                        value.attrib['ref_path'] = track.data[j].ref_path
                        value.attrib['ref_dti'] = RV_DTI_HASHES[track.data[j].ref_dti]

        if track.type in [3, 4, 5]:
            root.append(e)
        else:
            elements[track.parent - 1].append(e)
        elements.append(e)

    tree = ET.ElementTree(root)
    return tree


def from_xfs(xml, extension):
    root = ET.Element(
        'root',
        attrib={
            'extension': extension,
            'version_major': str(xml.header.version_major),
            'version_minor': str(xml.header.version_minor),
        },
    )

    if xml.data.num_roots != 1:
        raise ValueError(f'Expected one XFS root object, got {xml.data.num_roots}')

    def append_class(body, class_index, parent, object_index=None):
        class_def = xml.class_defs[class_index]
        class_name = RV_DTI_HASHES.get(class_def.type_hash, str(hex(class_def.type_hash)))
        class_attrib = {
            'name': class_name,
            'class_index': str(class_index),
        }
        if object_index is not None:
            class_attrib['object_index'] = str(object_index)
        class_xml = ET.SubElement(parent, 'class', attrib=class_attrib)

        for property_values in body.properties:
            prop = property_values.property
            prop_type = int(prop.type)
            prop_attrib = {
                'type': RV_MtPropertyType.get(prop_type, f'TYPE_UNKNOWN_{prop_type}'),
                'name': prop.name,
                'size': str(prop.size),
                'flags': str(prop.flags),
                'reserved': prop.reserved.hex(),
            }

            if prop_type in (1, 2):
                prop_xml = ET.SubElement(class_xml, 'classref', attrib=prop_attrib)
                for value in property_values.values:
                    if value.is_null:
                        ET.SubElement(
                            prop_xml,
                            'class',
                            attrib={
                                'name': 'null',
                                'reference_kind': 'null',
                            },
                        )
                    elif value.is_inline:
                        append_class(
                            value.body,
                            value.class_index,
                            prop_xml,
                            object_index=value.index,
                        )
                    else:
                        reference_class = xml.class_defs[value.class_index]
                        reference_name = RV_DTI_HASHES.get(
                            reference_class.type_hash,
                            str(hex(reference_class.type_hash)),
                        )
                        ET.SubElement(
                            prop_xml,
                            'class',
                            attrib={
                                'name': reference_name,
                                'class_index': str(value.class_index),
                                'reference_index': str(value.index),
                            },
                        )
            elif prop_type == int(xfs.Xfs.PropertyType.string):
                prop_xml = ET.SubElement(class_xml, 'string', attrib=prop_attrib)
                for value in property_values.values:
                    ET.SubElement(prop_xml, 'item', attrib={'val': value.value})
            elif prop_type == int(xfs.Xfs.PropertyType.resource):
                prop_xml = ET.SubElement(class_xml, 'resource', attrib=prop_attrib)
                for value in property_values.values:
                    ET.SubElement(prop_xml, 'item', attrib={'val': value.class_name})
                    ET.SubElement(prop_xml, 'item', attrib={'val': value.path})
            elif prop_type in mt.type_to_class:
                prop_xml = ET.SubElement(class_xml, 'vector', attrib=prop_attrib)
                for value in property_values.values:
                    vec_xml = ET.SubElement(prop_xml, 'vec')
                    if len(value.value) % 4:
                        raise ValueError(
                            f'XFS vector property {prop.name!r} has a value size '
                            f'of {len(value.value)} bytes, not divisible by 4'
                        )
                    for offset in range(0, len(value.value), 4):
                        component = struct.unpack_from('<f', value.value, offset)[0]
                        ET.SubElement(vec_xml, 'item', attrib={'val': str(component)})
            else:
                prop_xml = ET.SubElement(class_xml, 'scalar', attrib=prop_attrib)
                scalar_reader = mt.scalar_type_map.get(prop_type)
                for value in property_values.values:
                    if scalar_reader is None:
                        scalar_value = value.value.hex()
                    else:
                        scalar_value = str(
                            scalar_reader(KaitaiStream(io.BytesIO(value.value)))
                        )
                    ET.SubElement(prop_xml, 'item', attrib={'val': scalar_value})

    append_class(xml.data.root, 0, root, object_index=1)

    # Preserve class definitions that have no instantiated object in the XML
    # tree, along with the metadata needed to rebuild the class table exactly.
    metadata_xml = ET.SubElement(root, '_xfs_metadata')
    for class_index, class_def in enumerate(xml.class_defs):
        class_name = RV_DTI_HASHES.get(class_def.type_hash, str(hex(class_def.type_hash)))
        class_xml = ET.SubElement(
            metadata_xml,
            'class_def',
            attrib={
                'index': str(class_index),
                'name': class_name,
                'type_hash': str(class_def.type_hash),
            },
        )
        for prop in class_def.properties:
            ET.SubElement(
                class_xml,
                'property',
                attrib={
                    'name': prop.name,
                    'type_id': str(int(prop.type)),
                    'flags': str(prop.flags),
                    'size': str(prop.size),
                    'reserved': prop.reserved.hex(),
                },
            )

    tree = ET.ElementTree(root)
    return tree


def to_xfs(xml):
    """Serialize XFS XML using the class-definition/data-section schema."""
    if isinstance(xml, ET.ElementTree):
        xml = xml.getroot()
    if xml.tag != 'root':
        raise ValueError('XFS XML root must be <root>')

    root_classes = [child for child in xml if child.tag == 'class']
    if len(root_classes) != 1:
        raise ValueError(f'XFS XML must contain one root <class>, got {len(root_classes)}')
    root_class = root_classes[0]

    def parse_int(value):
        try:
            return int(value, 0)
        except ValueError:
            return int(value, 10)

    metadata_xml = xml.find('_xfs_metadata')
    class_defs = {}
    class_indexes_by_name = defaultdict(list)
    if metadata_xml is not None:
        for class_xml in metadata_xml.findall('class_def'):
            class_index = parse_int(class_xml.attrib['index'])
            class_name = class_xml.attrib['name']
            props = []
            for prop_xml in class_xml.findall('property'):
                reserved = bytes.fromhex(prop_xml.attrib.get('reserved', ''))
                if len(reserved) != 16:
                    raise ValueError(
                        f'XFS property {prop_xml.attrib.get("name")!r} '
                        'reserved field must be 16 bytes'
                    )
                props.append({
                    'name': prop_xml.attrib['name'],
                    'type_id': parse_int(prop_xml.attrib['type_id']),
                    'flags': parse_int(prop_xml.attrib.get('flags', '0')),
                    'size': parse_int(prop_xml.attrib['size']),
                    'reserved': reserved,
                })
            class_defs[class_index] = {
                'name': class_name,
                'type_hash': parse_int(class_xml.attrib['type_hash']),
                'properties': props,
            }
            class_indexes_by_name[class_name].append(class_index)

    def class_index_for_node(class_xml, create=False):
        if class_xml.attrib.get('name') == 'null':
            return None
        class_index_attr = class_xml.attrib.get('class_index')
        if class_index_attr is not None:
            class_index = parse_int(class_index_attr)
            if class_index not in class_defs and not create:
                raise ValueError(
                    f'XFS class {class_xml.attrib.get("name")!r} uses missing '
                    f'class index {class_index}'
                )
            return class_index

        class_name = class_xml.attrib['name']
        if class_indexes_by_name[class_name]:
            return class_indexes_by_name[class_name][0]
        if not create:
            raise ValueError(f'Unknown XFS class {class_name!r}')
        class_index = max(class_defs, default=-1) + 1
        class_indexes_by_name[class_name].append(class_index)
        return class_index

    def parse_property_type(prop_xml, old_prop=None):
        type_name = prop_xml.attrib.get('type')
        if type_name is None and old_prop is not None:
            return old_prop['type_id']
        try:
            return int(MtPropertyType[type_name])
        except (KeyError, TypeError):
            if type_name:
                try:
                    return parse_int(type_name)
                except ValueError:
                    pass
            if type_name and type_name.startswith('TYPE_UNKNOWN_'):
                try:
                    return parse_int(type_name[len('TYPE_UNKNOWN_'):])
                except ValueError:
                    pass
        raise ValueError(f'Unknown XFS property type {type_name!r}')

    fixed_property_sizes = {
        1: 4, 2: 4, 3: 1, 4: 1, 5: 2, 6: 4,
        8: 1, 9: 2, 10: 4, 12: 4, 14: 4, 15: 4,
        16: 8, 18: 16, 19: 64, 20: 16, 21: 16, 22: 16,
        36: 16, 47: 32, 54: 8, 55: 8, 57: 64, 58: 4,
    }

    def parse_property_def(prop_xml, old_prop=None):
        type_id = parse_property_type(prop_xml, old_prop)
        size_text = prop_xml.attrib.get('size')
        if size_text is not None:
            size = parse_int(size_text)
        elif old_prop is not None:
            size = old_prop['size']
        else:
            size = fixed_property_sizes.get(type_id, mt.scalar_bytes_num.get(type_id))
            if size is None and type_id in mt.type_to_class:
                vectors = prop_xml.findall('vec')
                size = len(vectors[0].findall('item')) * 4 if vectors else None
            if size is None:
                values = prop_xml.findall('item')
                if values:
                    try:
                        size = len(bytes.fromhex(values[0].attrib['val']))
                    except (KeyError, ValueError):
                        size = None
        if size is None:
            raise ValueError(
                f'Cannot determine XFS property size for {prop_xml.attrib.get("name")!r}'
            )

        if old_prop is not None:
            default_flags = old_prop['flags']
            default_reserved = old_prop['reserved']
        else:
            default_flags = 0
            default_reserved = bytes(16)
        flags_text = prop_xml.attrib.get('flags')
        flags = parse_int(flags_text) if flags_text is not None else default_flags
        reserved_text = prop_xml.attrib.get('reserved')
        reserved = bytes.fromhex(reserved_text) if reserved_text is not None else default_reserved
        if len(reserved) != 16:
            raise ValueError(
                f'XFS property {prop_xml.attrib.get("name")!r} reserved field must be 16 bytes'
            )
        return {
            'name': prop_xml.attrib.get('name', old_prop['name'] if old_prop else ''),
            'type_id': type_id,
            'flags': flags,
            'size': size,
            'reserved': reserved,
        }

    def hash_for_class(class_name):
        if class_name in DTI_HASHES:
            return DTI_HASHES[class_name]
        try:
            return parse_int(class_name)
        except ValueError:
            try:
                encoded = class_name.encode('ascii')
            except UnicodeEncodeError as error:
                raise ValueError(f'XFS class name {class_name!r} must be ASCII') from error
            return (~zlib.crc32(encoded)) & 0x7FFFFFFF

    seen_instance_defs = set()

    def collect_inline_classes(class_xml):
        class_index = class_index_for_node(class_xml, create=True)
        class_name = class_xml.attrib['name']
        old_def = class_defs.get(class_index)
        old_props = old_def['properties'] if old_def is not None else []
        property_nodes = list(class_xml)
        props = [
            parse_property_def(
                prop_xml,
                old_props[i] if i < len(old_props) else None,
            )
            for i, prop_xml in enumerate(property_nodes)
        ]

        if class_index in seen_instance_defs:
            current = class_defs[class_index]
            current_signature = [
                (p['name'], p['type_id'], p['flags'], p['size'], p['reserved'])
                for p in current['properties']
            ]
            new_signature = [
                (p['name'], p['type_id'], p['flags'], p['size'], p['reserved'])
                for p in props
            ]
            if current_signature != new_signature:
                raise ValueError(
                    f'Inconsistent property definitions for XFS class {class_name!r}'
                )
        else:
            if old_def is None:
                class_defs[class_index] = {
                    'name': class_name,
                    'type_hash': hash_for_class(class_name),
                    'properties': props,
                }
                if class_index not in class_indexes_by_name[class_name]:
                    class_indexes_by_name[class_name].append(class_index)
            else:
                old_def['name'] = class_name
                old_def['properties'] = props
            seen_instance_defs.add(class_index)

        for prop_xml in property_nodes:
            for value_xml in prop_xml.findall('class'):
                if (
                    value_xml.attrib.get('name') != 'null'
                    and 'reference_index' not in value_xml.attrib
                ):
                    collect_inline_classes(value_xml)

    collect_inline_classes(root_class)
    if class_index_for_node(root_class) != 0:
        raise ValueError('The root XFS object must use class index 0')

    if not class_defs:
        raise ValueError('XFS XML does not define any classes')
    class_count = max(class_defs) + 1
    if set(class_defs) != set(range(class_count)):
        raise ValueError('XFS class indexes must be contiguous from zero')
    if class_count > 0x7FFF:
        raise ValueError('XFS class count exceeds the object-reference tag capacity')

    def pack_uint(value, bits, label):
        limit = (1 << bits) - 1
        if not 0 <= value <= limit:
            raise ValueError(f'{label} {value} does not fit in {bits} bits')
        return value.to_bytes(bits // 8, 'little')

    def encode_ascii(value, label):
        if '\0' in value:
            raise ValueError(f'XFS {label} cannot contain NUL characters')
        try:
            return value.encode('ascii')
        except UnicodeEncodeError as error:
            raise ValueError(f'XFS {label} must be ASCII: {value!r}') from error

    def encode_terminated(value, label):
        return encode_ascii(value, label) + b'\0'

    scalar_formats = {
        3: 'B', 4: 'B', 5: 'H', 6: 'I', 7: 'Q',
        8: 'b', 9: 'h', 10: 'i', 11: 'q', 12: 'f', 13: 'd',
    }
    output_object_ids = {}
    next_object_id = 2

    def get_object_source_id(class_xml):
        value = class_xml.attrib.get('object_index')
        return parse_int(value) if value is not None else None

    root_source_id = get_object_source_id(root_class)
    output_object_ids[root_source_id if root_source_id is not None else 1] = 1

    def node_class_index(class_xml):
        class_index_attr = class_xml.attrib.get('class_index')
        if class_index_attr is not None:
            class_index = parse_int(class_index_attr)
        else:
            class_name = class_xml.attrib['name']
            options = class_indexes_by_name[class_name]
            if len(options) != 1:
                raise ValueError(f'Cannot resolve class index for XFS class {class_name!r}')
            class_index = options[0]
        if class_index not in class_defs:
            raise ValueError(f'XFS object uses undefined class index {class_index}')
        return class_index

    def encode_reference(class_xml):
        nonlocal next_object_id
        class_name = class_xml.attrib.get('name', '')
        if class_name == 'null' or class_xml.attrib.get('reference_kind') == 'null':
            return (
                pack_uint(0xFFFE, 16, 'null-reference tag')
                + pack_uint(0, 16, 'null-reference index')
            )

        class_index = node_class_index(class_xml)
        reference_source_id = class_xml.attrib.get('reference_index')
        if reference_source_id is not None:
            reference_source_id = parse_int(reference_source_id)
            if reference_source_id not in output_object_ids:
                raise ValueError(
                    f'XFS back-reference points to object {reference_source_id}, '
                    'which has not been serialized yet'
                )
            tag = class_index * 2
            object_index = output_object_ids[reference_source_id]
            return pack_uint(tag, 16, 'back-reference tag') + pack_uint(
                object_index, 16, 'back-reference index'
            )

        object_index = next_object_id
        next_object_id += 1
        source_id = get_object_source_id(class_xml)
        if source_id is not None:
            if source_id in output_object_ids:
                raise ValueError(f'Duplicate XFS object index {source_id}')
            output_object_ids[source_id] = object_index

        body = encode_body(class_xml, class_index)
        size = len(body) + 4
        return (
            pack_uint(class_index * 2 + 1, 16, 'inline-reference tag')
            + pack_uint(object_index, 16, 'inline-reference index')
            + pack_uint(size, 32, 'inline-reference size')
            + body
        )

    def encode_body(class_xml, class_index):
        class_def = class_defs[class_index]
        properties = list(class_xml)
        expected = class_def['properties']
        if len(properties) != len(expected):
            raise ValueError(
                f'XFS class {class_def["name"]!r} has {len(properties)} XML properties, '
                f'but its class definition has {len(expected)}'
            )

        output = bytearray()
        for prop_xml, prop_def in zip(properties, expected):
            type_id = prop_def['type_id']
            if prop_xml.attrib.get('name', '') != prop_def['name']:
                raise ValueError(
                    f'XFS property order/name mismatch in class {class_def["name"]!r}: '
                    f'{prop_xml.attrib.get("name")!r} != {prop_def["name"]!r}'
                )
            if type_id in (1, 2):
                values = prop_xml.findall('class')
                output.extend(pack_uint(len(values), 32, 'property value count'))
                for value_xml in values:
                    output.extend(encode_reference(value_xml))
            elif type_id == int(xfs.Xfs.PropertyType.string):
                values = prop_xml.findall('item')
                output.extend(pack_uint(len(values), 32, 'property value count'))
                for value_xml in values:
                    output.extend(encode_terminated(value_xml.attrib['val'], 'string value'))
            elif type_id == int(xfs.Xfs.PropertyType.resource):
                values = prop_xml.findall('item')
                if len(values) % 2:
                    raise ValueError(
                        f'XFS resource property {prop_def["name"]!r} must contain '
                        'class-name/path item pairs'
                    )
                output.extend(pack_uint(len(values) // 2, 32, 'property value count'))
                for i in range(0, len(values), 2):
                    output.extend(b'\x02')
                    output.extend(encode_terminated(values[i].attrib['val'], 'resource class name'))
                    output.extend(encode_terminated(values[i + 1].attrib['val'], 'resource path'))
            elif type_id in mt.type_to_class:
                values = prop_xml.findall('vec')
                output.extend(pack_uint(len(values), 32, 'property value count'))
                for vector_xml in values:
                    vector_data = bytearray()
                    for component in vector_xml.findall('item'):
                        vector_data.extend(struct.pack('<f', float(component.attrib['val'])))
                    if len(vector_data) != prop_def['size']:
                        raise ValueError(
                            f'XFS vector property {prop_def["name"]!r} has '
                            f'{len(vector_data)} bytes per value; expected {prop_def["size"]}'
                        )
                    output.extend(vector_data)
            else:
                values = prop_xml.findall('item')
                output.extend(pack_uint(len(values), 32, 'property value count'))
                value_format = scalar_formats.get(type_id)
                for value_xml in values:
                    value_text = value_xml.attrib['val']
                    if value_format is None:
                        try:
                            raw_value = bytes.fromhex(value_text)
                        except ValueError as error:
                            raise ValueError(
                                f'Unsupported XFS scalar type {type_id} needs a hex value'
                            ) from error
                        if len(raw_value) != prop_def['size']:
                            raise ValueError(
                                f'XFS raw property {prop_def["name"]!r} has '
                                f'{len(raw_value)} bytes; expected {prop_def["size"]}'
                            )
                        output.extend(raw_value)
                    else:
                        scalar_value = (
                            float(value_text)
                            if type_id in (12, 13)
                            else parse_int(value_text)
                        )
                        try:
                            raw_value = struct.pack('<' + value_format, scalar_value)
                        except (struct.error, OverflowError) as error:
                            raise ValueError(
                                f'Invalid value {value_text!r} for XFS property '
                                f'{prop_def["name"]!r}'
                            ) from error
                        if len(raw_value) != prop_def['size']:
                            raise ValueError(
                                f'XFS property {prop_def["name"]!r} encodes to '
                                f'{len(raw_value)} bytes; expected {prop_def["size"]}'
                            )
                        output.extend(raw_value)
        return bytes(output)

    root_class_index = node_class_index(root_class)
    root_body = encode_body(root_class, root_class_index)
    data_section = (
        pack_uint(1, 32, 'XFS root count')
        + pack_uint(len(root_body) + 4, 32, 'XFS data-section size')
        + root_body
    )

    name_table = bytearray()
    name_offsets = {}
    for class_index in range(class_count):
        for prop in class_defs[class_index]['properties']:
            prop_name = prop['name']
            if prop_name not in name_offsets:
                name_offsets[prop_name] = len(name_table)
                name_table.extend(encode_terminated(prop_name, 'property name'))

    offsets_size = class_count * 4
    class_defs_data = bytearray()
    class_def_offsets = []
    class_defs_size = sum(8 + 24 * len(class_defs[i]['properties']) for i in range(class_count))
    for class_index in range(class_count):
        class_def = class_defs[class_index]
        class_def_offsets.append(offsets_size + len(class_defs_data))
        class_defs_data.extend(pack_uint(class_def['type_hash'], 32, 'class type hash'))
        properties = class_def['properties']
        class_defs_data.extend(pack_uint(len(properties), 32, 'class property count'))
        for prop in properties:
            name_offset = offsets_size + class_defs_size + name_offsets[prop['name']]
            class_defs_data.extend(pack_uint(name_offset, 32, 'property name offset'))
            class_defs_data.extend(pack_uint(prop['type_id'], 8, 'property type'))
            class_defs_data.extend(pack_uint(prop['flags'], 8, 'property flags'))
            class_defs_data.extend(pack_uint(prop['size'], 16, 'property size'))
            class_defs_data.extend(prop['reserved'])

    extension = xml.attrib.get('extension', 'lot').lower().lstrip('.')
    extension_versions = {'fsm': 1, 'lot': 4, 'sce': 11, 'lnk': 14}
    if 'version_major' in xml.attrib:
        version_major = parse_int(xml.attrib['version_major'])
    else:
        version_major = 6
    if 'version_minor' in xml.attrib:
        version_minor = parse_int(xml.attrib['version_minor'])
    elif extension in extension_versions:
        version_minor = extension_versions[extension]
    else:
        raise ValueError(f'No XFS version is known for extension {extension!r}')

    offset_data = offsets_size + class_defs_size + len(name_table)
    header = (
        b'XFS\0'
        + pack_uint(version_major, 16, 'XFS major version')
        + pack_uint(version_minor, 16, 'XFS minor version')
        + pack_uint(class_count, 32, 'XFS class count')
        + pack_uint(offset_data, 32, 'XFS data offset')
    )
    class_def_offsets_data = b''.join(
        pack_uint(offset, 32, 'class-definition offset') for offset in class_def_offsets
    )
    return header + class_def_offsets_data + bytes(class_defs_data) + bytes(name_table) + data_section
