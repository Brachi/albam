import bpy
import bmesh
from math import ceil
from ..common_op import _get_mesh_albam_props
from mathutils import Vector, bvhtree


def _world_space_bmesh(obj, depsgraph):
    """Return the evaluated mesh of *obj* in the same (world) space as rays.

    ``BMesh.from_object`` produces coordinates local to the object.  The sorter
    casts rays from world-space vertices, so leaving a BVH in local space works
    only accidentally for objects with identity transforms.
    """
    bm = bmesh.new()
    bm.from_object(obj, depsgraph)
    bm.transform(obj.evaluated_get(depsgraph).matrix_world)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm


def _debug_draw_bvh_rays(rays, ob_name):
    rvis_name = ob_name + "_rays_viz"
    rviz_ob = bpy.data.objects.get(rvis_name, None)
    debug_collection = bpy.data.collections.get("DebugDraw")
    if debug_collection is None:
        debug_collection = bpy.data.collections.new("DebugDraw")
        bpy.context.scene.collection.children.link(debug_collection)

    if rviz_ob:
        rvis_mesh = rviz_ob.data
    else:
        rvis_mesh = bpy.data.meshes.new(rvis_name)
        rviz_ob = bpy.data.objects.new(rvis_name, rvis_mesh)
        debug_collection.objects.link(rviz_ob)

    bm_vis = bmesh.new()

    for origin, hit_loc in rays:
        v1 = bm_vis.verts.new(origin)
        v2 = bm_vis.verts.new(hit_loc)
        bm_vis.edges.new((v1, v2))

    bm_vis.to_mesh(rvis_mesh)
    bm_vis.free()


# Get minimal distance to the head
def _min_distance_to_target(obj, target_bvh):
    bm = _world_space_bmesh(obj, bpy.context.evaluated_depsgraph_get())
    min_dist = float('inf')
    for v in bm.verts:
        hit = target_bvh.find_nearest(v.co)
        if hit:
            loc, normal, index, dist = hit
            min_dist = min(min_dist, dist)
    return min_dist


def _get_blocked_objs(card_ob, v_from, v_to, bvh_list):
    '''Returns dictionary: {object: distance_to_hit}'''
    direction = (v_to - v_from).normalized()
    length = (v_to - v_from).length
    hit_objs = {}
    exclude_obj = []
    exclude_obj.append(card_ob)
    # Check if the ray the goes from card to body is blocked by other cards
    for bvh, target_ob in bvh_list:
        if target_ob in exclude_obj:
            continue
        hit = bvh.ray_cast(v_from, direction, length)
        location, normal, index, distance = hit
        if hit[0]:
            hit_objs[target_ob] = [distance * 100]  # scaling value not sure if needed
            exclude_obj.append(target_ob)
    return hit_objs


def _get_max_alpha_priority(cards_objs):
    max_aprior = 0
    for card_ob in cards_objs:
        custom_props = _get_mesh_albam_props(card_ob)
        if custom_props:
            if custom_props.alpha_priority > max_aprior:
                max_aprior = custom_props.alpha_priority
        else:
            if card_ob.get('order', 0) > max_aprior:
                max_aprior = card_ob.get('order', 0)
    return max_aprior


def _get_alpha_priority(card_ob):
    alpha_prior = 0
    custom_props = _get_mesh_albam_props(card_ob)
    if custom_props:
        alpha_prior = custom_props.alpha_priority
    else:
        alpha_prior = card_ob.get('order', 0)
    return alpha_prior


def _set_dbg_vtx_colors(bl_objects):
    max_alpha_pri = _get_max_alpha_priority(bl_objects)
    for i, obj in enumerate(bl_objects):
        if obj.type == 'MESH':
            cur_apha_pri = _get_alpha_priority(obj)
            mesh = obj.data
            if not mesh.vertex_colors:
                vcol_layer = mesh.vertex_colors.new(name="dbg_distance")
            else:
                vcol_layer = mesh.vertex_colors.active
            t = cur_apha_pri / max_alpha_pri if max_alpha_pri > 0 else 0
            color = (t, 0.0, 1.0 - t, 1.0)  # RGBA
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    vcol_layer.data[loop_index].color = color


def _nullify_alpha_prior(cards_objs):
    # Set alpha priority index to 0 for all hair cards
    for card_ob in cards_objs:
        custom_props = _get_mesh_albam_props(card_ob)
        if custom_props:
            custom_props.alpha_priority = 0
        card_ob['order'] = 0


def sort_hair_cards(body_ob, cards_objs):
    albam_settings = bpy.context.scene.albam.tools_settings
    debug_draw = albam_settings.sorting_dbg_draw

    deps = bpy.context.evaluated_depsgraph_get()
    # All BVHs and samples must use world coordinates.  The ray tests below
    # operate on world-space points, so a local-space BVH is inconsistent.
    body_bm = _world_space_bmesh(body_ob, deps)
    body_bvh = bvhtree.BVHTree.FromBMesh(body_bm)
    body_bm.free()

    # Build the BVH tree for cards
    bvh_list = []
    for card_ob in cards_objs:
        bm = _world_space_bmesh(card_ob, deps)
        bvh = bvhtree.BVHTree.FromBMesh(bm)
        bvh_list.append((bvh, card_ob))
        bm.free()

    def compute_blockers(card_ob, debug_draw=False):
        debug_rays = []

        bm = _world_space_bmesh(card_ob, deps)

        sample_points = []
        # Add vertices as sample points
        for v in bm.verts:
            sample_points.append(v.co.copy())
        # Add centers of faces as sample points
        for face in bm.faces:
            center = sum((v.co for v in face.verts), Vector()) / len(face.verts)
            sample_points.append(center)

        # Store both coverage and hit distance.  An isolated crossing of two
        # cards should not turn into a global ordering constraint for the
        # entire objects.
        blockers_cache = {}
        for world_v in sample_points:
            hit = body_bvh.find_nearest(world_v)
            if hit:
                loc, normal, index, dist = hit
                debug_rays.append((world_v, loc))
                # blocked_obj: distance
                blocked = _get_blocked_objs(card_ob, world_v, loc, bvh_list)
                if blocked:
                    for bobj, bdist in blocked.items():
                        blockers_cache[bobj] = blockers_cache.get(bobj, []) + bdist
        # A single hit is normally a local overlap, not evidence that one card
        # must be drawn in front of another.  Keep a constraint only when it
        # covers at least two samples or 20% of the card, whichever is lower.
        min_hits = min(2, max(1, ceil(len(sample_points) * 0.2)))
        blockers_cache = {
            obj: distances for obj, distances in blockers_cache.items()
            if len(distances) >= min_hits
        }
        # Prefer broad occlusion; use hit distance as a stable tie breaker.
        blocked_objs = sorted(
            blockers_cache,
            key=lambda obj: (-len(blockers_cache[obj]), sum(blockers_cache[obj]) / len(blockers_cache[obj])),
        )
        bm.free()
        print("Card {} is blocked by {}".format(card_ob.name, blocked_objs))
        if debug_draw:
            _debug_draw_bvh_rays(debug_rays, card_ob.name)
        evidence = {
            obj: {
                'coverage': len(distances) / len(sample_points),
                'distance': sum(distances) / len(distances),
            }
            for obj, distances in blockers_cache.items()
        }
        return blocked_objs, evidence

    def sorting_pass(cards_objs):
        # Collect blocker info for each card
        cards_objs_sorted = sorted(cards_objs, key=lambda o: _min_distance_to_target(o, body_bvh))
        _nullify_alpha_prior(cards_objs_sorted)

        card_info = {}  # {card_ob: {'distance': float, 'blockers': [list]}}
        for card_ob in cards_objs_sorted:
            dist = _min_distance_to_target(card_ob, body_bvh)
            blockers, blocker_evidence = compute_blockers(card_ob, debug_draw)
            card_info[card_ob] = {
                'distance': dist,
                'blockers': blockers,
                'blocker_evidence': blocker_evidence,
                'priority': 0
            }

        def _find_cycle(unassigned):
            """Return one cycle as ``(card, blocker)`` edges, if present."""
            state = {}
            path = []

            def visit(card_ob):
                state[card_ob] = 1
                path.append(card_ob)
                for blocker in card_info[card_ob]['blockers']:
                    if blocker not in unassigned:
                        continue
                    if state.get(blocker) == 1:
                        start = path.index(blocker)
                        nodes = path[start:] + [blocker]
                        return list(zip(nodes, nodes[1:]))
                    if state.get(blocker) is None:
                        cycle = visit(blocker)
                        if cycle:
                            return cycle
                path.pop()
                state[card_ob] = 2
                return None

            for card_ob in sorted(unassigned, key=lambda card: card.name):
                if state.get(card_ob) is None:
                    cycle = visit(card_ob)
                    if cycle:
                        return cycle
            return None

        # Topological sorting: priority = max(priority of blockers) + 1.
        # For a cycle, retain every card and remove only its weakest edge.
        unassigned = set(card_info)

        print("\n=== Topological Sorting ===")
        while unassigned:
            assigned_this_pass = False

            for card_ob in sorted(unassigned, key=lambda card: card.name):
                blockers = card_info[card_ob]['blockers']
                if not all(card_info[blocker]['priority'] > 0 for blocker in blockers):
                    continue
                priority = max((card_info[blocker]['priority'] for blocker in blockers), default=0) + 1
                card_info[card_ob]['priority'] = priority
                unassigned.remove(card_ob)
                assigned_this_pass = True

            if not assigned_this_pass:
                cycle = _find_cycle(unassigned)
                if not cycle:
                    raise RuntimeError("Unable to locate a cycle in the hair-card blocker graph")

                def edge_sort_key(edge):
                    card_ob, blocker = edge
                    evidence = card_info[card_ob]['blocker_evidence'][blocker]
                    # An edge pointing towards a card farther from the body is
                    # less plausible than one pointing towards a nearer card.
                    depth_conflict = card_info[card_ob]['distance'] <= card_info[blocker]['distance']
                    return evidence['coverage'], not depth_conflict, evidence['distance']

                card_ob, blocker = min(cycle, key=edge_sort_key)
                card_info[card_ob]['blockers'].remove(blocker)
                print(
                    "Cyclic intersection: removed weak edge {} -> {} (coverage {:.1%})".format(
                        card_ob.name,
                        blocker.name,
                        card_info[card_ob]['blocker_evidence'][blocker]['coverage'],
                    )
                )

        # Apply priorities to objects
        print("\n=== Final Priorities ===")
        for card_ob in cards_objs_sorted:
            priority = card_info[card_ob]['priority']
            blockers_count = len(card_info[card_ob]['blockers'])

            albam_props = _get_mesh_albam_props(card_ob)
            if albam_props:
                albam_props.alpha_priority = priority
            card_ob['order'] = priority

            print("{}: priority={}, blockers={} {}".format(
                card_ob.name,
                priority,
                blockers_count,
                [b.name for b in card_info[card_ob]['blockers']]
            ))

    sorting_pass(cards_objs)
    if debug_draw:
        _set_dbg_vtx_colors(cards_objs)
