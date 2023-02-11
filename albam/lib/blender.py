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
