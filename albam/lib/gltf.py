"""glTF 2.0 binary (.glb) reader and writer for albam.lib.scene.Scene.

Only what a scene holds is written: nodes, meshes, materials by name and
extras, skins with inverse bind matrices, and one scene listing the roots.
Reading accepts what Blender's exporter and this writer produce: a single
binary buffer, dense accessors (optionally strided and normalized), TRS or
matrix node transforms. Anything else raises rather than being silently
dropped.
"""
import json
import struct

import numpy as np

from .scene import Material, Mesh, Node, Primitive, Scene, Skin, decompose_trs

GLB_MAGIC = b"glTF"
GLB_VERSION = 2
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942

ARRAY_BUFFER = 34962
ELEMENT_ARRAY_BUFFER = 34963

COMPONENT_TYPES = {
    np.dtype("int8"): 5120,
    np.dtype("uint8"): 5121,
    np.dtype("int16"): 5122,
    np.dtype("uint16"): 5123,
    np.dtype("uint32"): 5125,
    np.dtype("float32"): 5126,
}
DTYPES = {code: dtype for dtype, code in COMPONENT_TYPES.items()}
ACCESSOR_TYPES = {1: "SCALAR", 2: "VEC2", 3: "VEC3", 4: "VEC4", 9: "MAT3", 16: "MAT4"}
COMPONENT_COUNTS = {name: count for count, name in ACCESSOR_TYPES.items()}

# Integer attributes glTF reads as fixed point in [0, 1]: everything but
# joint indices and face indices.
NORMALIZED_PREFIXES = ("TEXCOORD_", "COLOR_", "WEIGHTS_", "NORMAL", "TANGENT")


class _BufferBuilder:
    def __init__(self):
        self.data = bytearray()
        self.views = []
        self.accessors = []

    def accessor(self, array, target=None, minmax=False, normalized=False):
        array = np.ascontiguousarray(array)
        if array.ndim == 1:
            components = 1
        elif array.ndim == 2:
            components = array.shape[1]
        elif array.ndim == 3:
            # a stack of matrices: glTF wants each one column major
            components = array.shape[1] * array.shape[2]
            array = np.ascontiguousarray(array.transpose(0, 2, 1)).reshape(array.shape[0], components)
        else:
            raise ValueError(f"cannot store an array of shape {array.shape}")
        if array.dtype not in COMPONENT_TYPES:
            raise ValueError(f"glTF has no component type for {array.dtype}")

        self.data.extend(b"\0" * (-len(self.data) % 4))
        view = {"buffer": 0, "byteOffset": len(self.data), "byteLength": array.nbytes}
        if target is not None:
            view["target"] = target
        self.data.extend(array.tobytes())
        self.views.append(view)

        accessor = {
            "bufferView": len(self.views) - 1,
            "componentType": COMPONENT_TYPES[array.dtype],
            "count": int(array.shape[0]),
            "type": ACCESSOR_TYPES[components],
        }
        if normalized:
            accessor["normalized"] = True
        if minmax:
            accessor["min"] = array.min(axis=0).reshape(-1).tolist()
            accessor["max"] = array.max(axis=0).reshape(-1).tolist()
        self.accessors.append(accessor)
        return len(self.accessors) - 1


def _attribute_array(name, array):
    """The dtype an attribute is stored with: joints as unsigned shorts,
    indices as the narrowest unsigned type, everything else float32."""
    array = np.asarray(array)
    if name.startswith("JOINTS_"):
        return array.astype(np.uint16, copy=False)
    return array.astype(np.float32, copy=False)


def _clean_extras(value):
    """JSON-compatible copy of an extras value. numpy scalars and arrays,
    bytes and tuples become plain Python; anything else is an error here
    rather than at json.dumps, where the message names no key."""
    if isinstance(value, dict):
        return {str(k): _clean_extras(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean_extras(v) for v in value]
    if isinstance(value, np.ndarray):
        return _clean_extras(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, bytes):
        return list(value)
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(f"extras value {value!r} of type {type(value).__name__} is not JSON compatible")


def write_glb(scene, include_materials=True):
    """The scene as .glb bytes."""
    builder = _BufferBuilder()
    document = {
        "asset": {"version": "2.0", "generator": scene.generator},
        "scene": 0,
        "scenes": [{"nodes": list(scene.roots)}],
        "nodes": [],
        "meshes": [],
    }

    for mesh in scene.meshes:
        primitives = []
        for primitive in mesh.primitives:
            attributes = {}
            for name, array in primitive.attributes.items():
                array = _attribute_array(name, array)
                attributes[name] = builder.accessor(array, ARRAY_BUFFER, minmax=(name == "POSITION"))
            entry = {"attributes": attributes, "mode": primitive.mode}
            if primitive.indices is not None:
                indices = np.asarray(primitive.indices)
                dtype = np.uint16 if len(indices) == 0 or indices.max() < 0xFFFF else np.uint32
                entry["indices"] = builder.accessor(indices.astype(dtype), ELEMENT_ARRAY_BUFFER)
            if include_materials and primitive.material is not None:
                entry["material"] = primitive.material
            primitives.append(entry)
        entry = {"name": mesh.name, "primitives": primitives}
        if mesh.extras:
            entry["extras"] = _clean_extras(mesh.extras)
        document["meshes"].append(entry)

    if include_materials and scene.materials:
        document["materials"] = []
        for material in scene.materials:
            entry = {
                "name": material.name,
                "pbrMetallicRoughness": {"metallicFactor": 0.0},
                "doubleSided": material.double_sided,
            }
            if material.extras:
                entry["extras"] = _clean_extras(material.extras)
            document["materials"].append(entry)

    for node in scene.nodes:
        entry = {"name": node.name}
        if np.any(node.translation != 0):
            entry["translation"] = [float(c) for c in node.translation]
        if np.any(node.rotation != (0, 0, 0, 1)):
            entry["rotation"] = [float(c) for c in node.rotation]
        if np.any(node.scale != 1):
            entry["scale"] = [float(c) for c in node.scale]
        if node.children:
            entry["children"] = list(node.children)
        if node.mesh is not None:
            entry["mesh"] = node.mesh
        if node.skin is not None:
            entry["skin"] = node.skin
        if node.extras:
            entry["extras"] = _clean_extras(node.extras)
        document["nodes"].append(entry)

    if scene.skins:
        document["skins"] = []
        for skin in scene.skins:
            entry = {"joints": list(skin.joints)}
            if skin.name:
                entry["name"] = skin.name
            if skin.skeleton is not None:
                entry["skeleton"] = skin.skeleton
            if skin.inverse_bind_matrices is not None:
                entry["inverseBindMatrices"] = builder.accessor(
                    np.asarray(skin.inverse_bind_matrices, dtype=np.float32))
            document["skins"].append(entry)

    document["buffers"] = [{"byteLength": len(builder.data)}]
    document["bufferViews"] = builder.views
    document["accessors"] = builder.accessors

    json_chunk = json.dumps(document, separators=(",", ":")).encode("utf-8")
    json_chunk += b" " * (-len(json_chunk) % 4)
    bin_chunk = bytes(builder.data) + b"\0" * (-len(builder.data) % 4)
    total = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
    return b"".join((
        struct.pack("<4sII", GLB_MAGIC, GLB_VERSION, total),
        struct.pack("<II", len(json_chunk), CHUNK_JSON), json_chunk,
        struct.pack("<II", len(bin_chunk), CHUNK_BIN), bin_chunk,
    ))


def _split_glb(data):
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != GLB_MAGIC or version != GLB_VERSION:
        raise ValueError("not a glTF 2.0 binary")
    offset = 12
    document = None
    binary = b""
    while offset < length:
        chunk_length, chunk_type = struct.unpack_from("<II", data, offset)
        chunk = data[offset + 8:offset + 8 + chunk_length]
        if chunk_type == CHUNK_JSON:
            document = json.loads(chunk.decode("utf-8"))
        elif chunk_type == CHUNK_BIN:
            binary = chunk
        offset += 8 + chunk_length
    if document is None:
        raise ValueError("glb has no JSON chunk")
    return document, binary


class _Reader:
    def __init__(self, document, binary):
        self.document = document
        self.binary = binary
        if len(document.get("buffers", [])) > 1 or any("uri" in b for b in document.get("buffers", [])):
            raise ValueError("only a single embedded buffer is supported")

    def accessor(self, index, normalize=False):
        accessor = self.document["accessors"][index]
        if "sparse" in accessor or "bufferView" not in accessor:
            raise ValueError("sparse and bufferless accessors are not supported")
        view = self.document["bufferViews"][accessor["bufferView"]]
        dtype = DTYPES[accessor["componentType"]]
        components = COMPONENT_COUNTS[accessor["type"]]
        count = accessor["count"]
        element_size = dtype.itemsize * components
        stride = view.get("byteStride", element_size)
        start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        if stride == element_size:
            array = np.frombuffer(self.binary, dtype=dtype, count=count * components, offset=start)
        else:
            raw = np.frombuffer(self.binary, dtype=np.uint8, count=stride * (count - 1) + element_size,
                                offset=start)
            strided = np.lib.stride_tricks.as_strided(
                raw, shape=(count, element_size), strides=(stride, 1))
            array = np.ascontiguousarray(strided).view(dtype)
        array = array.reshape(count, components) if components > 1 else array.reshape(count)
        if accessor["type"] == "MAT4":
            # column major in the file, mathematical convention in the scene
            array = array.reshape(count, 4, 4).transpose(0, 2, 1)
        if normalize and (accessor.get("normalized") or dtype.kind in "iu") and dtype.kind != "f":
            array = array.astype(np.float32) / np.iinfo(dtype).max
        return np.array(array)


def read_glb(data):
    """A Scene from .glb bytes."""
    document, binary = _split_glb(data)
    reader = _Reader(document, binary)
    scene = Scene(generator=document.get("asset", {}).get("generator", ""))

    for entry in document.get("materials", []):
        scene.materials.append(Material(
            name=entry.get("name", ""),
            extras=entry.get("extras", {}),
            double_sided=entry.get("doubleSided", False),
        ))

    for entry in document.get("meshes", []):
        primitives = []
        for primitive in entry["primitives"]:
            attributes = {}
            for name, accessor_index in primitive["attributes"].items():
                normalize = name.startswith(NORMALIZED_PREFIXES) or name.startswith("_")
                attributes[name] = reader.accessor(accessor_index, normalize=normalize)
            indices = None
            if "indices" in primitive:
                indices = reader.accessor(primitive["indices"]).astype(np.uint32)
            primitives.append(Primitive(
                attributes=attributes,
                indices=indices,
                material=primitive.get("material"),
                mode=primitive.get("mode", 4),
            ))
        scene.meshes.append(Mesh(name=entry.get("name", ""), primitives=primitives,
                                 extras=entry.get("extras", {})))

    for entry in document.get("nodes", []):
        node = Node(name=entry.get("name", ""))
        if "matrix" in entry:
            matrix = np.array(entry["matrix"], dtype=np.float64).reshape(4, 4).T
            node.translation, node.rotation, node.scale = decompose_trs(matrix)
        else:
            node.translation = np.array(entry.get("translation", (0, 0, 0)), dtype=np.float64)
            node.rotation = np.array(entry.get("rotation", (0, 0, 0, 1)), dtype=np.float64)
            node.scale = np.array(entry.get("scale", (1, 1, 1)), dtype=np.float64)
        node.children = list(entry.get("children", []))
        node.mesh = entry.get("mesh")
        node.skin = entry.get("skin")
        node.extras = entry.get("extras", {})
        scene.nodes.append(node)

    for entry in document.get("skins", []):
        inverse_bind_matrices = None
        if "inverseBindMatrices" in entry:
            inverse_bind_matrices = reader.accessor(entry["inverseBindMatrices"])
        scene.skins.append(Skin(
            joints=list(entry["joints"]),
            inverse_bind_matrices=inverse_bind_matrices,
            skeleton=entry.get("skeleton"),
            name=entry.get("name", ""),
        ))

    scenes = document.get("scenes", [])
    if scenes:
        scene.roots = list(scenes[document.get("scene", 0)].get("nodes", []))
    else:
        children = {child for node in scene.nodes for child in node.children}
        scene.roots = [index for index in range(len(scene.nodes)) if index not in children]
    return scene
