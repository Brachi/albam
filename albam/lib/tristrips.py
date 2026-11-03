from collections import deque


def strip_triangles_to_triangles_list(strip_indices_array):
    indices = []

    for i in range(2, len(strip_indices_array)):
        a = strip_indices_array[i - 2]
        b = strip_indices_array[i - 1]
        c = strip_indices_array[i]
        if a != b and a != c and b != c:
            if i % 2 == 0:
                indices.extend((a, b, c))
            else:
                indices.extend((c, b, a))
    if not indices:
        return list(strip_indices_array)
    return indices


def _triangle_edge_keys(triangle):
    a, b, c = triangle
    return (
        tuple(sorted((a, b))),
        tuple(sorted((b, c))),
        tuple(sorted((c, a))),
    )


def triangles_list_to_triangles_strip(triangles):
    """
    Convert a flat list of triangles (3-tuples of vertex indices, already
    triangulated) into one or more triangle strips, joined by degenerate
    triangles into a single index list.
    Takes plain vertex-index triangles rather than a blender mesh object, so
    the caller controls what a "vertex index" means (e.g. a post-split index
    that is no longer 1:1 with `mesh.vertices`).
    Based on a paper by Pierre Terdiman: http://www.codercorner.com/Strips.htm
    """
    # TODO: Fix changing of face orientation in some cases (see tests)
    triangles = [tuple(t) for t in triangles]
    edges_faces = {}
    current_strip = []
    strips = []
    joined_strips = []
    faces_indices = deque(range(len(triangles)))
    done_faces_indices = set()
    current_face_index = faces_indices.popleft()
    process_faces = True

    for face_index, triangle in enumerate(triangles):
        for edge in _triangle_edge_keys(triangle):
            edges_faces.setdefault(edge, set()).add(face_index)

    while process_faces:
        current_face_verts = triangles[current_face_index]
        strip_indices = [v for v in current_face_verts if v not in current_strip[-2:]]
        if current_strip:
            face_to_add = tuple(current_strip[-2:]) + tuple(strip_indices)
            if face_to_add != current_face_verts and face_to_add != tuple(reversed(current_face_verts)):
                # we arrived here because the current face shares and edge with the face in the strip
                # however, if we just add the verts, we would be changing the direction of the face
                # so we create a degenerate triangle before adding to it to the strip
                current_strip.append(current_strip[-2])
        current_strip.extend(strip_indices)
        done_faces_indices.add(current_face_index)

        next_face_index = None
        possible_face_indices = {}
        for edge in _triangle_edge_keys(current_face_verts):
            if edge not in edges_faces:
                continue
            checked_edge = {face_index: edge for face_index in edges_faces[edge]
                            if face_index != current_face_index and face_index not in done_faces_indices}
            possible_face_indices.update(checked_edge)
        for face_index, edge in possible_face_indices.items():
            if not current_strip:
                next_face_index = face_index
                break
            elif edge == tuple(current_strip[-2:]) or edge == tuple(reversed(current_strip[-2:])):
                next_face_index = face_index
                break
            elif edge == (current_strip[-1], current_strip[-2]):
                if len(current_strip) % 2 != 0:
                    # create a degenerate triangle to join them
                    current_strip.append(current_strip[-2])
                next_face_index = face_index

        if next_face_index:
            faces_indices.remove(next_face_index)
            current_face_index = next_face_index
        else:
            strips.append(current_strip)
            current_strip = []
            try:
                current_face_index = faces_indices.popleft()
            except IndexError:
                process_faces = False

    prev_strip_len = 0
    # join strips with degenerate triangles
    for strip in strips:
        if not prev_strip_len:
            joined_strips.extend(strip)
            prev_strip_len = len(strip)
        elif prev_strip_len % 2 == 0:
            joined_strips.extend((joined_strips[-1], strip[0]))
            joined_strips.extend(strip)
            prev_strip_len = len(strip)
        else:
            joined_strips.extend((joined_strips[-1], strip[0], strip[0]))
            joined_strips.extend(strip)
            prev_strip_len = len(strip)

    return joined_strips
