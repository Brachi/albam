import array

import requests

import bpy

normals = [(str(i) + '--->', list(map(lambda n: round(n * 127), vert.normal))) for i, vert in enumerate(D.meshes[1].vertices)]


def load_mesh(vertex_locations, faces, per_vertex_normals):
    mesh = bpy.data.meshes.new('test')
    ob = bpy.data.objects.new('test', mesh)

    mesh.from_pydata(vertex_locations, [], faces)

    mesh.create_normals_split()

    #for loop in mesh.loops:
    #    loop.normal[:] = per_vertex_normals[loop.vertex_index]
    for vert in mesh.vertices:
        vert.normal[:] = per_vertex_normals[vert.index]

    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=True)

    #clnors = array.array('f', [0.0] * (len(mesh.loops) * 3))
    #mesh.loops.foreach_get("normal", clnors)

    #mesh.normals_split_custom_set(tuple(zip(*(iter(clnors),) * 3)))
    mesh.normals_split_custom_set_from_vertices(per_vertex_normals)
    mesh.use_auto_smooth = True
    mesh.show_edge_sharp = True

    bpy.context.scene.objects.link(ob)

    return mesh


def main():
    DATA_SOURCE = 'https://pastebin.com/raw/RRzmNgwd'
    data = requests.get(DATA_SOURCE).json()

    vertex_locations = data['locations']
    faces = data['faces']
    per_vertex_normals = data['normals']

    mesh = load_mesh(vertex_locations, faces, per_vertex_normals)

if __name__ == '__main__':
    main()

