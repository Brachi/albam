"""
Debug-only ASCII tree printer for an fs.base.FS instance (MTFW_FS in
particular) - lets a human eyeball what the current tree representation
actually looks like. origin_of() already returns a game-root-relative
identity, so no extra path processing is needed here.
"""
from fs.path import join


def format_tree(fs_instance, path="/", max_depth=None, max_entries_per_dir=None, show_origin=True):
    """max_depth/max_entries_per_dir=None means unlimited (full dump)."""
    lines = []
    _format_tree(fs_instance, path, max_depth, max_entries_per_dir, show_origin, "", 0, lines)
    return "\n".join(lines)


def _format_tree(fs_instance, path, max_depth, max_entries_per_dir, show_origin, prefix, depth, lines):
    if max_depth is not None and depth > max_depth:
        lines.append(prefix + "└── ... (max depth reached)")
        return

    entries = sorted(
        fs_instance.scandir(path, namespaces=("basic",)),
        key=lambda info: (not info.is_dir, info.name.lower()),
    )
    shown = entries if max_entries_per_dir is None else entries[:max_entries_per_dir]
    remainder = len(entries) - len(shown)

    for i, info in enumerate(shown):
        is_last_shown = i == len(shown) - 1
        is_truly_last = is_last_shown and remainder == 0
        connector = "└── " if is_truly_last else "├── "
        child_path = join(path, info.name)

        if info.is_dir:
            lines.append(prefix + connector + info.name + "/")
            extension = "    " if is_truly_last else "│   "
            _format_tree(
                fs_instance, child_path, max_depth, max_entries_per_dir,
                show_origin, prefix + extension, depth + 1, lines,
            )
        else:
            tag = ""
            if show_origin and hasattr(fs_instance, "origin_of"):
                origin = fs_instance.origin_of(child_path)
                tag = f"  [archived: {origin}]" if origin else "  [loose]"
            lines.append(prefix + connector + info.name + tag)

    if remainder > 0:
        lines.append(prefix + f"└── ... {remainder} more")
