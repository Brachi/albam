import bpy
import bmesh
from kaitaistruct import KaitaiStream
import math
from collections import defaultdict
from io import BytesIO
from .structs.nav_156 import Nav156
from ...registry import blender_registry
from ...vfs import VirtualFileData, VirtualFile
from .collision import palette

KNOWN_FACE_FLAGS = [0, 256, 2048, 2049, 2050, 2560, 3072, 3584, 4096, 4098, 4608, 5120, 5124, 6144, 6145,
                    6146, 6656, 7168, 7172, 7176, 7680, 8448, 8452, 8456, 24832, 41216, 134144, 134656,
                    138240, 138752, 145664, 155904, 172288, 175872, 179968, 8390656, 8391168, 8397056,
                    8528128, 12591360]


@blender_registry.register_import_function(app_id="re5", extension="nav", albam_asset_type="NAVMESH")
def build_navmesh_model(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
    assert app_id == "re5", f"The game {app_id} is not supported yet"
    nav_bytes = vfile.get_bytes()
    ModCls = Nav156
    nav = ModCls.from_bytes(nav_bytes)
    nav._read()

    bl_object_name = vfile.display_name
    bl_object = bpy.data.objects.new(bl_object_name, None)

    me_ob = bpy.data.meshes.new(bl_object_name)
    ob = bpy.data.objects.new(bl_object_name, me_ob)

    vertices = []
    faces = []
    face_flags = {}
    for i, vtx in enumerate(nav.vertices):
        vertices.append((vtx.x/100, -vtx.z/100, vtx.y/100))
    for i, face in enumerate(nav.faces):
        faces.append((face.v1, face.v2, face.v3))
        face_flags[face.index] = face.unk2
    me_ob.from_pydata(vertices, [], faces)
    _set_flags_as_mat(me_ob, face_flags)
    ob.parent = bl_object

    return bl_object


@blender_registry.register_export_function(app_id="re5", extension="nav")
def export_nav(bl_obj):
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    dst_nav = Nav156()
    vertices = []
    faces = []
    vfiles = []

    meshes = [c for c in bl_obj.children_recursive if c.type == "MESH"]
    if meshes:
        for v in meshes[0].data.vertices:
            vertices.append(v.co)
        for poly in meshes[0].data.polygons:
            faces.append(poly.vertices[:])
            # print("Polygon", poly.index, "uses vertices", poly.vertices[:])
    neiborgs = build_neighbors(vertices, faces)

    dst_nav.magic = b"NAV\x00"
    dst_nav.version = 2
    dst_nav.reserved = 0
    dst_nav.vertex_count = len(vertices)
    dst_nav.face_count = len(faces)
    dst_nav.header_padding = 1
    dst_vertices = []
    dst_faces = []
    size_vertices = 0
    for vtx in vertices:
        dst_vtx = dst_nav.Vertex(_parent=dst_nav, _root=dst_nav._root)
        dst_vtx.x = vtx[0] * 100
        dst_vtx.y = -vtx[2] * 100
        dst_vtx.z = vtx[1] * 100
        dst_vertices.append(dst_vtx)
        size_vertices += 12
    dst_nav.vertices = dst_vertices
    size_faces = 0
    for face_index, face in enumerate(faces):
        dst_face = dst_nav.Face(_parent=dst_nav, _root=dst_nav._root)
        dst_face.index = face_index
        dst_face.unk1 = 1
        dst_face.unk2 = 0  # flags
        dst_face.vertex_per_face = 3
        dst_face.v1 = face[0]
        dst_face.v2 = face[1]
        dst_face.v3 = face[2]
        dst_face.neighbor_count = len(neiborgs[face_index])
        size_faces += (32 + len(neiborgs[face_index]) * 16)
        dst_face_neighbors = []
        for neighbor_index, edge_id, distance in neiborgs[face_index]:
            dst_neigborg = dst_nav.Neighbor(_parent=dst_face, _root=dst_nav._root)
            dst_neigborg.face_index = neighbor_index
            dst_neigborg.padding = 0
            dst_neigborg.edge = edge_id
            dst_neigborg.centroid_distance = distance
            dst_face_neighbors.append(dst_neigborg)
        dst_face.neighbors = dst_face_neighbors
        dst_face._check()
        dst_faces.append(dst_face)
    dst_nav.faces = dst_faces
    lower, upper = bounding_box(vertices)
    dst_bbox = dst_nav.BoundingBox(_parent=dst_nav, _root=dst_nav._root)
    dst_bbox.padding0 = 0
    dst_lower = dst_nav.Vertex(_parent=dst_bbox, _root=dst_nav._root)
    dst_lower.x = lower[0] * 100
    dst_lower.y = lower[2] * 100
    dst_lower.z = lower[1] * 100
    dst_bbox.lower = dst_lower
    dst_bbox.padding1 = b"\xCD\xCD\xCD\xCD"
    dst_upper = dst_nav.Vertex(_parent=dst_bbox, _root=dst_nav._root)
    dst_upper.x = upper[0] * 100
    dst_upper.y = upper[2] * 100
    dst_upper.z = upper[1] * 100
    dst_bbox.upper = dst_upper
    dst_bbox.padding2 = b"\xCD\xCD\xCD\xCD"
    dst_bbox._check()
    dst_nav.bbox = dst_bbox
    dst_nav.footer_magic = b"\x07\x55\x15\x00\x00"
    dst_nav.footer_padding = b"\x00" * 5460
    dst_grid, size_grid = write_lookup_grid(dst_nav, vertices, faces, lower, upper)
    dst_nav.lookup_grid = dst_grid
    final_size = sum((24, size_vertices, size_faces, 36, 5, 5460, size_grid))
    stream = KaitaiStream(BytesIO(bytearray(final_size)))
    dst_nav._check()
    dst_nav._write(stream)
    nav_vf = VirtualFileData(app_id, asset.relative_path, data_bytes=stream.to_byte_array())
    vfiles.append(nav_vf)
    return vfiles


def _set_flags_as_mat(mesh, flags):
    unique_flags = []
    for flag in flags.values():
        if flag not in unique_flags:
            unique_flags.append(flag)

    mat_cache = {}
    for i, uf in enumerate(unique_flags):
        mat = bpy.data.materials.new(name="Nav %03d" % uf)
        try:
            mat.diffuse_color = palette[KNOWN_FACE_FLAGS.index(uf)]
        except (IndexError, ValueError):
            mat.diffuse_color = (0, 0, 0, 1)
            print("Unknown nav type: %d" % uf)
        mesh.materials.append(mat)
        mat_cache[uf] = i
    bm = bmesh.new()
    bm.from_mesh(mesh)
    for face in bm.faces:
        face.material_index = mat_cache.get(flags[face.index], 0)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    # print(sorted(unique_flags))


def bounding_box(vertices):

    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]

    return (
        (min(xs), min(ys), min(zs)),
        (max(xs), max(ys), max(zs))
    )


def centroid(vertices, face):
    a, b, c = face

    ax, ay, az = vertices[a]
    bx, by, bz = vertices[b]
    cx, cy, cz = vertices[c]

    return (
        (ax + bx + cx) / 3.0,
        (ay + by + cy) / 3.0,
        (az + bz + cz) / 3.0,
    )


def build_neighbors(vertices, faces):
    edge_map = defaultdict(list)

    edge_ids = [
        (0, 1),  # edge 0 = v1-v2
        (1, 2),  # edge 1 = v2-v3
        (0, 2),  # edge 2 = v1-v3
    ]

    for face_index, face in enumerate(faces):
        for edge_id, (i, j) in enumerate(edge_ids):
            a = face[i]
            b = face[j]
            key = tuple(sorted((a, b)))
            edge_map[key].append((face_index, edge_id))

    centroids = [centroid(vertices, face) for face in faces]

    neighbors = [[] for _ in faces]

    for edge, refs in edge_map.items():
        if len(refs) != 2:
            continue
        (f0, e0), (f1, e1) = refs
        c0 = centroids[f0]
        c1 = centroids[f1]
        dist = math.sqrt((c0[0]-c1[0])**2 + (c0[1]-c1[1])**2 + (c0[2]-c1[2])**2)
        neighbors[f0].append((f1, e0, dist))
        neighbors[f1].append((f0, e1, dist))

    for n in neighbors:
        n.sort(key=lambda x: x[0])

    return neighbors


def part1by1(n):
    n &= 0xFFFF
    n = (n | (n << 8)) & 0x00FF00FF
    n = (n | (n << 4)) & 0x0F0F0F0F
    n = (n | (n << 2)) & 0x33333333
    n = (n | (n << 1)) & 0x55555555
    return n


def morton2D(x, z):
    return part1by1(x) | (part1by1(z) << 1)


def write_lookup_grid(dst_nav, vertices, faces, lower, upper):
    dst_grid_cells = []
    GRID_SIZE = 64

    min_x, _, min_z = lower
    max_x, _, max_z = upper

    width = max_x - min_x
    depth = max_z - min_z

    # Avoid divide-by-zero on flat meshes
    if width == 0:
        width = 1.0

    if depth == 0:
        depth = 1.0

    cell_w = width / GRID_SIZE
    cell_d = depth / GRID_SIZE

    # One list of face indices for each cell
    grid = [[] for _ in range(GRID_SIZE * GRID_SIZE)]

    for face_index, face in enumerate(faces):

        xs = [vertices[i][0] for i in face]
        zs = [vertices[i][2] for i in face]

        tri_min_x = min(xs)
        tri_max_x = max(xs)

        tri_min_z = min(zs)
        tri_max_z = max(zs)

        cell_min_x = int((tri_min_x - min_x) / cell_w)
        cell_max_x = int((tri_max_x - min_x) / cell_w)

        cell_min_z = int((tri_min_z - min_z) / cell_d)
        cell_max_z = int((tri_max_z - min_z) / cell_d)

        # Clamp to valid range
        cell_min_x = max(0, min(63, cell_min_x))
        cell_max_x = max(0, min(63, cell_max_x))

        cell_min_z = max(0, min(63, cell_min_z))
        cell_max_z = max(0, min(63, cell_max_z))

        for z in range(cell_min_z, cell_max_z + 1):
            for x in range(cell_min_x, cell_max_x + 1):

                morton = morton2D(x, z)

                grid[morton].append(face_index)

    # Write cells
    dst_grid_size = 0
    for faces_in_cell in grid:
        faces_in_cell.sort()
        dst_cell = dst_nav.GridCell(_parent=dst_nav, _root=dst_nav._root)
        dst_grid_size += 4
        dst_faces = []
        dst_cell.face_count = len(faces_in_cell)
        for face_index in faces_in_cell:
            dst_face = dst_nav.GridFace(_parent=dst_cell, _root=dst_nav._root)
            dst_face.face_index = face_index
            dst_face.padding = 0
            dst_faces.append(dst_face)
            dst_grid_size += 8
        dst_cell.faces = dst_faces
        dst_cell._check()
        dst_grid_cells.append(dst_cell)
    return dst_grid_cells, dst_grid_size
