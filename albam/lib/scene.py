"""The in-memory scene every engine decodes into and serializes from.

It is glTF 2.0's data model with numpy arrays in place of accessors: nodes in
a hierarchy with TRS transforms, meshes made of primitives whose attributes
are named the glTF way (POSITION, NORMAL, TEXCOORD_0, JOINTS_0, ...), skins
with inverse bind matrices, and `extras` dicts for what glTF has no field
for. Units are metres, Y up, right handed; quaternions are xyzw. Nothing here
imports bpy, so a parser can be tested against this without Blender.
"""
from dataclasses import dataclass, field

import numpy as np


# Where albam keeps engine data a glTF consumer has no use for, at every
# level (root node, joint node, mesh, material). One key, so a file written
# by albam and re-read by albam cannot confuse its own data with a user's
# custom properties, which Blender's glTF exporter also puts in extras.
EXTRAS_KEY = "ALBAM"

# Per-vertex attribute naming the source vertex an exported vertex came from,
# for a writer that wants one vertex per source vertex and attribute set
# rather than one per corner (see albam.lib.gltf_blender.export_objects).
VERTEX_ATTRIBUTE = "_ALBAM_VERTEX"

# glTF primitive modes
TRIANGLES = 4


def quaternion_to_matrix(q):
    x, y, z, w = (float(c) for c in q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ], dtype=np.float64)


def matrix_to_quaternion(m):
    """xyzw quaternion of a 3x3 rotation matrix (no scale)."""
    m = np.asarray(m, dtype=np.float64)
    trace = m[0, 0] + m[1, 1] + m[2, 2]
    if trace > 0:
        s = np.sqrt(trace + 1.0) * 2
        return np.array([(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s,
                         (m[1, 0] - m[0, 1]) / s, 0.25 * s])
    if m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        return np.array([0.25 * s, (m[0, 1] + m[1, 0]) / s,
                         (m[0, 2] + m[2, 0]) / s, (m[2, 1] - m[1, 2]) / s])
    if m[1, 1] > m[2, 2]:
        s = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        return np.array([(m[0, 1] + m[1, 0]) / s, 0.25 * s,
                         (m[1, 2] + m[2, 1]) / s, (m[0, 2] - m[2, 0]) / s])
    s = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
    return np.array([(m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s,
                     0.25 * s, (m[1, 0] - m[0, 1]) / s])


def compose_trs(translation, rotation, scale):
    m = np.eye(4, dtype=np.float64)
    m[:3, :3] = quaternion_to_matrix(rotation) * np.asarray(scale, dtype=np.float64)
    m[:3, 3] = translation
    return m


def decompose_trs(m):
    """(translation, xyzw rotation, scale) of a 4x4 affine matrix, assuming no shear."""
    m = np.asarray(m, dtype=np.float64)
    translation = m[:3, 3].copy()
    scale = np.linalg.norm(m[:3, :3], axis=0)
    if np.linalg.det(m[:3, :3]) < 0:
        scale[0] = -scale[0]
    rotation = matrix_to_quaternion(m[:3, :3] / scale)
    return translation, rotation, scale


@dataclass
class Primitive:
    # name -> (N, components) array; names and layouts follow glTF
    attributes: dict
    # (M,) triangle list indices into the attributes, or None for a point cloud
    indices: np.ndarray | None = None
    material: int | None = None
    mode: int = TRIANGLES

    @property
    def vertex_count(self):
        return len(self.attributes["POSITION"])


@dataclass
class Mesh:
    name: str
    primitives: list
    extras: dict = field(default_factory=dict)


@dataclass
class Material:
    name: str
    extras: dict = field(default_factory=dict)
    double_sided: bool = True


@dataclass
class Skin:
    # node indices, in joint order (JOINTS_n values index this list)
    joints: list
    # (J, 4, 4) float32, mathematical convention: M @ column vector
    inverse_bind_matrices: np.ndarray | None = None
    skeleton: int | None = None
    name: str = ""


@dataclass
class Node:
    name: str
    translation: np.ndarray = field(default_factory=lambda: np.zeros(3))
    rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0, 1.0]))
    scale: np.ndarray = field(default_factory=lambda: np.ones(3))
    children: list = field(default_factory=list)
    mesh: int | None = None
    skin: int | None = None
    extras: dict = field(default_factory=dict)

    @property
    def local_matrix(self):
        return compose_trs(self.translation, self.rotation, self.scale)


@dataclass
class Scene:
    nodes: list = field(default_factory=list)
    meshes: list = field(default_factory=list)
    materials: list = field(default_factory=list)
    skins: list = field(default_factory=list)
    # indices of the nodes with no parent
    roots: list = field(default_factory=list)
    generator: str = "albam"

    def add_node(self, node, parent=None):
        self.nodes.append(node)
        index = len(self.nodes) - 1
        if parent is None:
            self.roots.append(index)
        else:
            self.nodes[parent].children.append(index)
        return index

    def add_mesh(self, mesh):
        self.meshes.append(mesh)
        return len(self.meshes) - 1

    def add_material(self, material):
        self.materials.append(material)
        return len(self.materials) - 1

    def add_skin(self, skin):
        self.skins.append(skin)
        return len(self.skins) - 1

    def parent_of(self, index):
        for parent_index, node in enumerate(self.nodes):
            if index in node.children:
                return parent_index
        return None

    def parents(self):
        """node index -> parent node index, None for a root."""
        parents = {index: None for index in range(len(self.nodes))}
        for parent_index, node in enumerate(self.nodes):
            for child in node.children:
                parents[child] = parent_index
        return parents

    def world_matrix(self, index, up_to=None):
        """Transform of node `index`, accumulated from the root or from the
        node `up_to` (excluded), the way a joint's position is read relative
        to its armature."""
        parents = self.parents()
        matrix = np.eye(4)
        while index is not None and index != up_to:
            matrix = self.nodes[index].local_matrix @ matrix
            index = parents[index]
        return matrix

    def walk(self, index=None):
        """Node indices depth first, children in order."""
        indices = self.roots if index is None else self.nodes[index].children
        for child in indices:
            yield child
            yield from self.walk(child)

    def mesh_nodes(self):
        return [index for index in self.walk() if self.nodes[index].mesh is not None]

    def node_named(self, name):
        for index, node in enumerate(self.nodes):
            if node.name == name:
                return index
        raise KeyError(name)
