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
        return blocked_objs, {obj: len(distances) for obj, distances in blockers_cache.items()}

    def sorting_pass(cards_objs):
        # Collect blocker info for each card
        cards_objs_sorted = sorted(cards_objs, key=lambda o: _min_distance_to_target(o, body_bvh))
        _nullify_alpha_prior(cards_objs_sorted)

        card_info = {}  # {card_ob: {'distance': float, 'blockers': [list]}}
        for card_ob in cards_objs_sorted:
            dist = _min_distance_to_target(card_ob, body_bvh)
            blockers, blocker_hits = compute_blockers(card_ob, debug_draw)
            card_info[card_ob] = {
                'distance': dist,
                'blockers': blockers,
                'blocker_hits': blocker_hits,
                'priority': 0
            }

        # Intersecting cards can make A block B and B block A.  A single alpha
        # priority per object cannot represent that geometry exactly, but a
        # directed graph is still possible when the weaker direction is
        # discarded.  For equal evidence, favour the card nearer to the body.
        for card_ob, info in card_info.items():
            for blocker in list(info['blockers']):
                if card_ob not in card_info[blocker]['blockers']:
                    continue
                card_hits = info['blocker_hits'][blocker]
                blocker_hits = card_info[blocker]['blocker_hits'][card_ob]
                remove_from = blocker if card_hits > blocker_hits else card_ob
                if card_hits == blocker_hits:
                    remove_from = blocker if info['distance'] <= card_info[blocker]['distance'] else card_ob
                card_info[remove_from]['blockers'].remove(
                    blocker if remove_from == card_ob else card_ob
                )

        def _get_total_blocker_depth(card_ob, visited=None):
            """Recursively count total blocker depth including blockers of blockers"""
            if visited is None:
                visited = set()
            if card_ob in visited:
                return 0
            visited.add(card_ob)
            blockers = card_info[card_ob]['blockers']
            total = len(blockers)
            for blocker in blockers:
                total += _get_total_blocker_depth(blocker, visited)
            return total

        # Check for intersections of cards (cycles in blocker dependencies)
        print("\n=== Checking for Intersections ===")
        for card_ob in card_info.keys():
            blockers = card_info[card_ob]['blockers']
            # Check if any blocker has this card in its blockers (direct cycle)
            for blocker in blockers:
                if card_ob in card_info[blocker]['blockers']:
                    print("WARNING: Intersection detected between {} and {}".format(
                        card_ob.name, blocker.name))

        # Topological sorting: priority = max(priority of blockers) + 1
        # Iterate until all priorities are assigned
        max_iterations = len(cards_objs) + 1
        iteration = 0
        unassigned = set(card_info.keys())

        print("\n=== Topological Sorting ===")
        while unassigned and iteration < max_iterations:
            iteration += 1
            assigned_this_pass = False

            for card_ob in sorted(list(unassigned), key=lambda c: _get_total_blocker_depth(c)):
                blockers = card_info[card_ob]['blockers']

                # check if all blockers have priority assigned
                all_blockers_assigned = all(card_info[blocker]['priority'] > 0 for blocker in blockers)

                if not blockers:
                    # No blockers - priority 1
                    card_info[card_ob]['priority'] = 1
                    assigned_this_pass = True
                    unassigned.remove(card_ob)
                    print("Pass {}: {} - no blockers → priority=1".format(iteration, card_ob.name))

                elif all_blockers_assigned:
                    # All blockers have priority - take max + 1
                    max_blocker_priority = max(card_info[b]['priority'] for b in blockers)
                    priority = max_blocker_priority + 1
                    card_info[card_ob]['priority'] = priority
                    assigned_this_pass = True
                    unassigned.remove(card_ob)
                    print("Pass {}: {} - max(blockers)={} → priority={}".format(
                        iteration, card_ob.name, max_blocker_priority, priority))

            if not assigned_this_pass and unassigned:
                # A true geometry intersection can form a longer dependency
                # cycle.  Break just one weakest-in-practice constraint and
                # continue sorting the rest, instead of assigning every card
                # in the cycle an arbitrary priority in one fallback pass.
                cycle_breaker = min(unassigned, key=lambda c: card_info[c]['distance'])
                cyclic_blockers = [
                    blocker for blocker in card_info[cycle_breaker]['blockers']
                    if blocker in unassigned
                ]
                card_info[cycle_breaker]['blockers'] = [
                    blocker for blocker in card_info[cycle_breaker]['blockers']
                    if blocker not in unassigned
                ]
                print(
                    "Warning: cyclic intersections detected. Removing {} blockers from {}."
                    .format(len(cyclic_blockers), cycle_breaker.name)
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
