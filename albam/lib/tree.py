import copy
import os


class Tree:
    PATH_SEPARATOR = "::"

    def __init__(self, root_id=None):
        self.root = []
        self.root_id = root_id
        self.nodes = {}

    def _find_node_in_level(self, node_name, node_level):
        node_found = None
        for node in node_level:
            if node["name"] == node_name:
                node_found = node
                break
        return node_found

    def add_node_from_path(self, full_path, path_separator="\\"):
        path_parts = full_path.split(path_separator)
        leaf_name = path_parts[-1]

        current_level = 0
        current_dir = self.root
        ancestors_ids = [] if not self.root_id else [self.root_id]
        for i in range(len(path_parts) - 1):
            path_part = path_parts[i]
            existing_node = self._find_node_in_level(node_name=path_part, node_level=current_dir)
            if existing_node:
                new_node = existing_node
            else:
                new_node = {
                    "name": path_part,
                    "extension": os.path.splitext(path_part)[1].replace(".", ""),
                    "children": [],
                    "depth": current_level,
                    "node_id": self.generate_node_id(path_parts[0 : i + 1]),
                    "ancestors_ids": copy.copy(ancestors_ids),
                }
                current_dir.append(new_node)
                self.nodes[new_node["node_id"]] = new_node

            ancestors_ids.append(new_node["node_id"])
            current_level += 1
            current_dir = new_node["children"]

        node_id = self.generate_node_id(path_parts)
        leaf_node = {
            "name": leaf_name,
            "extension": os.path.splitext(leaf_name)[1].replace(".", ""),
            "children": [],
            "depth": current_level,
            "node_id": node_id,
            "ancestors_ids": ancestors_ids,
        }
        current_dir.append(leaf_node)
        self.nodes[node_id] = leaf_node

    def generate_node_id(self, parts):
        prefix = (self.root_id or "") + self.PATH_SEPARATOR
        body = self.PATH_SEPARATOR.join(parts)
        return prefix + body

    @staticmethod
    def sort_node(node):
        """
        Sort expandable items first
        """
        return node['name'] if node['children'] else "zzz" + node['name']

    def flatten(self, flat_tree=None, current_level=None):
        flat_tree = flat_tree or []
        current_level = current_level or self.root

        for node in sorted(current_level, key=self.sort_node):
            flat_tree.append(node)
            if node['children']:
                self.flatten(flat_tree, node['children'])
        return flat_tree
