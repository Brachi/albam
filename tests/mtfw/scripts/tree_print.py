"""
Debug-only ASCII tree printer for an fs.base.FS instance (MTFW_FS in
particular) - lets a human eyeball what the current tree representation
actually looks like, including today's absolute-path leak in origin_of()
for archived files, before/after changing it.
"""
import os

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
                tag = f"  [archived: {_relative_origin(origin, fs_instance)}]" if origin else "  [loose]"
            lines.append(prefix + connector + info.name + tag)

    if remainder > 0:
        lines.append(prefix + f"└── ... {remainder} more")


def _relative_origin(origin, fs_instance):
    game_root = getattr(fs_instance, "game_root", None)
    if not game_root:
        return origin
    try:
        return os.path.relpath(origin, game_root).replace(os.sep, "/")
    except ValueError:
        # e.g. game_root is an s3:// URI (MTFW_FS.from_s3) - relpath doesn't
        # apply, fall back to showing the raw origin as-is.
        return origin
