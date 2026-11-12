"""Graph helpers for RE5 CHN ChainInfo topology."""


def _ordered(values, order):
    return sorted(values, key=lambda value: (order.get(value, len(order)), value))


def decompose_edges(nodes, edges):
    """Turn an undirected graph into deterministic, edge-disjoint strands.

    CHN stores adjacency on each joint. Import treats an edge present in either
    endpoint's slots as a graph edge, while the raw slots remain available for
    lossless export until the graph is edited.
    """
    nodes = list(dict.fromkeys(nodes))
    order = {node: index for index, node in enumerate(nodes)}
    adjacency = {node: set() for node in nodes}
    for left, right in edges:
        if left not in adjacency or right not in adjacency or left == right:
            continue
        adjacency[left].add(right)
        adjacency[right].add(left)

    components = []
    unseen = set(nodes)
    while unseen:
        start = min(unseen, key=lambda node: order[node])
        stack, component = [start], set()
        unseen.remove(start)
        while stack:
            node = stack.pop()
            component.add(node)
            for neighbor in _ordered(adjacency[node] & unseen, order):
                unseen.remove(neighbor)
                stack.append(neighbor)
        components.append(component)

    strands = []
    for component in components:
        if not any(adjacency[node] for node in component):
            node = next(iter(component))
            strands.append({"joints": [node], "closed": False})
            continue

        used = set()

        def edge_key(left, right):
            return frozenset((left, right))

        def walk(start, first):
            path = [start, first]
            used.add(edge_key(start, first))
            current = first
            while len(adjacency[current]) == 2:
                candidates = [
                    node for node in _ordered(adjacency[current], order)
                    if edge_key(current, node) not in used
                ]
                if not candidates:
                    break
                nxt = candidates[0]
                used.add(edge_key(current, nxt))
                current = nxt
                if current == start:
                    path.append(current)
                    break
                path.append(current)
            return path

        # Start trails at every non-degree-two vertex. Forks therefore appear
        # at the ends of multiple strands, and every edge is consumed once.
        branch_nodes = _ordered(
            (node for node in component if len(adjacency[node]) != 2), order)
        for node in branch_nodes:
            for neighbor in _ordered(adjacency[node], order):
                if edge_key(node, neighbor) not in used:
                    strands.append({"joints": walk(node, neighbor), "closed": False})

        # Remaining edges form cycles. Walk one complete cycle per component.
        while True:
            remaining = [
                (node, neighbor)
                for node in component
                for neighbor in adjacency[node]
                if edge_key(node, neighbor) not in used
            ]
            if not remaining:
                break
            start = min((pair[0] for pair in remaining), key=lambda node: order[node])
            first = min(
                (neighbor for neighbor in adjacency[start]
                 if edge_key(start, neighbor) not in used),
                key=lambda node: order[node],
            )
            cycle = [start]
            previous, current = start, first
            used.add(edge_key(previous, current))
            while current != start:
                cycle.append(current)
                candidates = [
                    node for node in _ordered(adjacency[current], order)
                    if node != previous and edge_key(current, node) not in used
                ]
                if not candidates:
                    break
                previous, current = current, candidates[0]
                used.add(edge_key(previous, current))
            strands.append({"joints": cycle, "closed": current == start})

    strands.sort(key=lambda strand: min(order[node] for node in strand["joints"]))
    return strands


def links_from_strands(strands):
    """Return the symmetric adjacency sets represented by strand sequences."""
    links = {}
    for strand in strands:
        joints = list(strand.get("joints", ()))
        for node in joints:
            links.setdefault(node, set())
        for left, right in zip(joints, joints[1:]):
            if left != right:
                links.setdefault(left, set()).add(right)
                links.setdefault(right, set()).add(left)
        if strand.get("closed") and len(joints) > 2 and joints[-1] != joints[0]:
            links.setdefault(joints[-1], set()).add(joints[0])
            links.setdefault(joints[0], set()).add(joints[-1])
    return links


def ordered_links_from_strands(strands, raw_links=None):
    """Compile strands, retaining source edge direction where it is known.

    Strand-authored edges that did not exist in the source are emitted both
    ways. Existing one-way source edges remain one-way while they remain in a
    strand, so editing an unrelated part of a graph does not rewrite them.
    """
    raw_links = raw_links or {}
    ordered_links = {}
    pairs = []
    seen_pairs = set()

    def add_pair(left, right):
        if left == right:
            return
        pair = frozenset((left, right))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            pairs.append((left, right))
        ordered_links.setdefault(left, [])
        ordered_links.setdefault(right, [])

    for strand in strands:
        joints = list(strand.get("joints", ()))
        for node in joints:
            ordered_links.setdefault(node, [])
        for left, right in zip(joints, joints[1:]):
            add_pair(left, right)
        if strand.get("closed") and len(joints) > 2:
            add_pair(joints[-1], joints[0])

    for left, right in pairs:
        forward = right in raw_links.get(left, ())
        backward = left in raw_links.get(right, ())
        if forward or backward:
            if forward:
                ordered_links[left].append(right)
            if backward:
                ordered_links[right].append(left)
        else:
            ordered_links[left].append(right)
            ordered_links[right].append(left)
    return ordered_links


def remove_node_from_strands(strands, node):
    """Remove a joint and its incident edges, splitting open paths as needed."""
    result = []
    for strand in strands:
        joints = list(strand.get("joints", ()))
        if node not in joints:
            result.append({"joints": joints, "closed": bool(strand.get("closed"))})
            continue
        if strand.get("closed") and len(joints) > 1:
            index = joints.index(node)
            remaining = joints[index + 1:] + joints[:index]
            if remaining:
                result.append({"joints": remaining, "closed": False})
            continue
        current = []
        for joint in joints:
            if joint == node:
                if current:
                    result.append({"joints": current, "closed": False})
                    current = []
            else:
                current.append(joint)
        if current:
            result.append({"joints": current, "closed": False})
    return result
