"""Curses TUI for adding/removing entries in tests/mtfw/datasets/*_hashes.json.

Point it at a local game install and browse that install's MTFW_FS tree; the
files you pick are committed as hashes only, never as plain-text game asset
paths (see tests/mtfw/scripts/catalog_paths.py for why). Maintainer/owner
tool, same as tests/mtfw/scripts/generate_catalog.py - it needs a real game
install, and nothing in CI runs it.

Usage (from the repo root):

    python tests/tools/dataset_editor.py <app-id> <game-root>

Example:

    python tests/tools/dataset_editor.py umvc3 "/path/to/UMVC3"

Keys:
    up/down, j/k     move            pgup/pgdn, ctrl-u/d  page
    space, enter     toggle: expand/collapse a directory, add/remove a file
    right/l          expand dir      left/h               collapse dir / go to parent
    1..9             (multi-hash datasets) assign the file to that hash slot
    a                (multi-hash datasets) commit the staged slots as one entry
    e                switch between the tree and the dataset's entry list
    d                (entry list) remove the entry under the cursor
    /                filter by name, n/N jump between matches
    tab              switch dataset
    w                write the dataset back to disk
    q                quit (asks first if there are unsaved changes)
"""
import argparse
import curses
import json
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _REPO_ROOT)

from albam.engines.mtfw.arc_fs import MTFW_FS  # noqa: E402
from tests.mtfw.scripts.catalog_paths import hash_virtual_path  # noqa: E402

DATASETS_DIR = os.path.join(_REPO_ROOT, "tests", "mtfw", "datasets")

# Every dataset is a list of {"app_id": ..., "<something>_path_hash": ...}
# objects, but which hash keys an entry needs is the dataset's own schema -
# lmt_import needs an lmt *and* the mod it animates, mrl_serialization a mrl
# *and* its mod. Read from the file's existing entries when possible (the
# dataset itself is the source of truth), with this as the fallback for a
# dataset that's empty or doesn't exist yet.
KNOWN_SCHEMAS = {
    "lmt_import_hashes.json": ("lmt_path_hash", "mod_path_hash"),
    "mrl_serialization_hashes.json": ("mrl_path_hash", "mod_path_hash"),
}

# hash key -> the extension a file assigned to that slot is expected to
# have. Only a warning: a dataset is free to point at something unusual,
# and the extension is not what makes the entry valid.
EXPECTED_EXTENSIONS = {
    "lmt_path_hash": "lmt",
    "mod_path_hash": "mod",
    "mrl_path_hash": "mrl",
    "nav_path_hash": "nav",
    "rtex_path_hash": "rtex",
    "sbc_path_hash": "sbc",
    "tex_path_hash": "tex",
}


class Dataset:
    """One tests/mtfw/datasets/*_hashes.json file, plus what's staged for it."""

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        with open(path) as f:
            self.entries = json.load(f)
        self.hash_keys = self._infer_hash_keys()
        self.dirty = False
        # hash key -> (hash, path), for building a multi-hash entry one file
        # at a time. Always empty for a single-hash dataset, where a pick is
        # a whole entry on its own.
        self.staged = {}

    def _infer_hash_keys(self):
        keys = []
        for entry in self.entries:
            for key in entry:
                if key != "app_id" and key not in keys:
                    keys.append(key)
        return tuple(keys) or KNOWN_SCHEMAS.get(self.name) or ("mod_path_hash",)

    @property
    def is_multi(self):
        return len(self.hash_keys) > 1

    def hashes_for(self, app_id, key):
        return {e[key] for e in self.entries if e["app_id"] == app_id and key in e}

    def all_hashes(self, app_id):
        return {h for key in self.hash_keys for h in self.hashes_for(app_id, key)}

    def find(self, app_id, values):
        """Index of the entry matching app_id + every hash in values, or None."""
        for i, entry in enumerate(self.entries):
            if entry.get("app_id") != app_id:
                continue
            if all(entry.get(key) == value for key, value in values.items()):
                return i
        return None

    def add(self, app_id, values):
        if self.find(app_id, values) is not None:
            return False
        entry = {"app_id": app_id}
        entry.update({key: values[key] for key in self.hash_keys})
        self.entries.append(entry)
        self.dirty = True
        return True

    def remove_index(self, index):
        self.entries.pop(index)
        self.dirty = True

    def save(self):
        # Match what's already committed: 4-space indent for the *_hashes
        # datasets (generate_catalog.py writes the catalogs with 2), and a
        # trailing newline, so saving a file this tool didn't change
        # produces no diff.
        with open(self.path, "w") as f:
            json.dump(self.entries, f, indent=4)
            f.write("\n")
        self.dirty = False


class TreeNode:
    def __init__(self, path, name, is_dir, depth, parent=None):
        self.path = path
        self.name = name
        self.is_dir = is_dir
        self.depth = depth
        self.parent = parent
        self.expanded = False
        self.children = None  # None until the directory is first expanded
        self._hash = None

    @property
    def hash(self):
        if self._hash is None:
            self._hash = hash_virtual_path(self.path)
        return self._hash


class Tree:
    """Lazily-expanded view of an MTFW_FS instance.

    A full game install is ~100k entries across a thousand-odd archives, so
    directories are only scanned when they're first expanded, and a path is
    only hashed when it becomes visible.
    """

    def __init__(self, game_fs):
        self.game_fs = game_fs
        self.root = TreeNode("/", "/", True, -1)
        self.root.expanded = True
        self._load_children(self.root)

    def _load_children(self, node):
        if node.children is not None:
            return
        try:
            infos = sorted(
                self.game_fs.scandir(node.path, namespaces=("basic",)),
                key=lambda info: (not info.is_dir, info.name.lower()),
            )
        except Exception:  # unreadable archive, permissions, a broken entry
            infos = []
        base = node.path.rstrip("/")
        node.children = [
            TreeNode(f"{base}/{info.name}", info.name, info.is_dir, node.depth + 1, node)
            for info in infos
        ]

    def expand(self, node):
        if node.is_dir:
            self._load_children(node)
            node.expanded = True

    def visible(self):
        rows = []
        stack = list(reversed(self.root.children or []))
        while stack:
            node = stack.pop()
            rows.append(node)
            if node.is_dir and node.expanded and node.children:
                stack.extend(reversed(node.children))
        return rows


class App:
    TREE, ENTRIES = "tree", "entries"

    def __init__(self, stdscr, app_id, game_fs, datasets, catalog_hashes):
        self.stdscr = stdscr
        self.app_id = app_id
        self.tree = Tree(game_fs)
        self.datasets = datasets
        self.dataset_index = 0
        self.catalog_hashes = catalog_hashes
        self.mode = self.TREE
        self.cursor = 0
        self.top = 0
        self.entry_cursor = 0
        self.entry_top = 0
        self.status = "space toggles, w writes, q quits - full key list in the docstring"
        self.filter = ""
        self.rows = self.tree.visible()

    @property
    def dataset(self):
        return self.datasets[self.dataset_index]

    # -- actions ---------------------------------------------------------

    def toggle_dir(self, node):
        if node.expanded:
            node.expanded = False
        else:
            self.tree.expand(node)

    def toggle_file(self, node):
        dataset = self.dataset
        if dataset.is_multi:
            self.status = (
                f"{dataset.name} needs {len(dataset.hash_keys)} hashes per entry - "
                f"assign with 1..{len(dataset.hash_keys)}, then press a"
            )
            return
        key = dataset.hash_keys[0]
        index = dataset.find(self.app_id, {key: node.hash})
        if index is not None:
            dataset.remove_index(index)
            self.status = f"removed {node.name} ({node.hash})"
        else:
            dataset.add(self.app_id, {key: node.hash})
            self.status = f"added {node.name} ({node.hash}){self._warnings(key, node)}"

    def assign_slot(self, node, slot):
        dataset = self.dataset
        if slot >= len(dataset.hash_keys):
            return
        key = dataset.hash_keys[slot]
        dataset.staged[key] = (node.hash, node.path)
        missing = [k for k in dataset.hash_keys if k not in dataset.staged]
        suffix = f"; still need {', '.join(missing)}" if missing else "; press a to add"
        self.status = f"{key} = {node.name}{self._warnings(key, node)}{suffix}"

    def commit_staged(self):
        dataset = self.dataset
        missing = [k for k in dataset.hash_keys if k not in dataset.staged]
        if missing:
            self.status = f"nothing added - still missing {', '.join(missing)}"
            return
        values = {key: value[0] for key, value in dataset.staged.items()}
        if dataset.add(self.app_id, values):
            self.status = "added " + ", ".join(
                f"{k}={v[0]}" for k, v in dataset.staged.items())
            dataset.staged.clear()
        else:
            self.status = "that entry is already in the dataset"

    def _warnings(self, key, node):
        """Flag the two things a wrong pick usually is: an unexpected
        extension for the slot, and a file the committed catalog doesn't
        know about - which is what test_dataset_hashes_are_in_catalog will
        fail on later, so it's worth saying now rather than at test time.
        """
        notes = []
        expected = EXPECTED_EXTENSIONS.get(key)
        actual = node.name.rsplit(".", 1)[-1].lower() if "." in node.name else ""
        if expected and actual != expected:
            notes.append(f"not a .{expected}")
        if self.catalog_hashes is not None and node.hash not in self.catalog_hashes:
            notes.append(f"NOT in {self.app_id}_catalog.json")
        return f" [{'; '.join(notes)}]" if notes else ""

    def remove_entry(self):
        dataset = self.dataset
        if not dataset.entries:
            return
        entry = dataset.entries[self.entry_cursor]
        dataset.remove_index(self.entry_cursor)
        self.entry_cursor = min(self.entry_cursor, max(len(dataset.entries) - 1, 0))
        self.status = "removed " + ", ".join(
            f"{k}={v}" for k, v in entry.items() if k != "app_id")

    def save(self):
        dirty = [d for d in self.datasets if d.dirty]
        for dataset in dirty:
            dataset.save()
        self.status = (
            "wrote " + ", ".join(d.name for d in dirty) if dirty else "nothing to write"
        )

    def search(self, start, step):
        if not self.filter:
            return
        needle = self.filter.lower()
        for offset in range(1, len(self.rows) + 1):
            i = (start + offset * step) % len(self.rows)
            if needle in self.rows[i].name.lower():
                self.cursor = i
                return
        self.status = f"no match for {self.filter!r} among the expanded rows"

    # -- drawing ---------------------------------------------------------

    def draw(self):
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()
        body_height = max(height - 3, 1)

        self._draw_header(width)
        if self.mode == self.TREE:
            self._draw_tree(body_height, width)
        else:
            self._draw_entries(body_height, width)
        self._addstr(height - 1, 0, self.status[:width - 1], curses.A_DIM)
        self.stdscr.refresh()

    def _draw_header(self, width):
        dataset = self.dataset
        marker = "*" if dataset.dirty else " "
        slots = ""
        if dataset.is_multi:
            slots = "  slots: " + " ".join(
                f"{i + 1}:{key.split('_')[0]}"
                f"{'=' + dataset.staged[key][0][:8] if key in dataset.staged else ''}"
                for i, key in enumerate(dataset.hash_keys)
            )
        header = (
            f"{self.app_id}  {marker}{dataset.name} "
            f"({len(dataset.entries)} entries, {len(dataset.all_hashes(self.app_id))} "
            f"for {self.app_id}){slots}"
        )
        self._addstr(0, 0, header[:width - 1], curses.A_REVERSE)
        mode = "tree" if self.mode == self.TREE else "entries"
        hint = f"[{mode}]  tab: dataset  e: switch view  w: write  q: quit"
        self._addstr(1, 0, hint[:width - 1], curses.A_DIM)

    def _draw_tree(self, body_height, width):
        self.rows = self.tree.visible()
        self.cursor = max(0, min(self.cursor, len(self.rows) - 1))
        self.top = max(min(self.top, self.cursor), self.cursor - body_height + 1)
        in_dataset = self.dataset.all_hashes(self.app_id)

        for i in range(body_height):
            index = self.top + i
            if index >= len(self.rows):
                break
            node = self.rows[index]
            if node.is_dir:
                mark, name = ("-" if node.expanded else "+"), node.name + "/"
            else:
                mark = "x" if node.hash in in_dataset else " "
                name = node.name
            line = f" [{mark}] {'  ' * node.depth}{name}"
            if not node.is_dir:
                line += f"   {node.hash}"
            attr = curses.A_REVERSE if index == self.cursor else curses.A_NORMAL
            self._addstr(2 + i, 0, line[:width - 1].ljust(width - 1), attr)

    def _draw_entries(self, body_height, width):
        entries = self.dataset.entries
        self.entry_cursor = max(0, min(self.entry_cursor, len(entries) - 1))
        self.entry_top = max(
            min(self.entry_top, self.entry_cursor), self.entry_cursor - body_height + 1)
        for i in range(body_height):
            index = self.entry_top + i
            if index >= len(entries):
                break
            entry = entries[index]
            hashes = "  ".join(
                f"{k.split('_')[0]}:{v}" for k, v in entry.items() if k != "app_id")
            line = f" {entry.get('app_id', '?'):<8} {hashes}"
            attr = curses.A_REVERSE if index == self.entry_cursor else curses.A_NORMAL
            if entry.get("app_id") != self.app_id:
                attr |= curses.A_DIM
            self._addstr(2 + i, 0, line[:width - 1].ljust(width - 1), attr)

    def _addstr(self, y, x, text, attr=curses.A_NORMAL):
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:  # writing the last cell of the screen always raises
            pass

    def prompt(self, question):
        height, width = self.stdscr.getmaxyx()
        curses.echo()
        self._addstr(height - 1, 0, " " * (width - 1))
        self._addstr(height - 1, 0, question)
        try:
            answer = self.stdscr.getstr(height - 1, len(question) + 1, 60).decode()
        finally:
            curses.noecho()
        return answer

    # -- main loop -------------------------------------------------------

    def run(self):
        while True:
            self.draw()
            key = self.stdscr.getch()
            if key in (ord("q"), 27):
                if any(d.dirty for d in self.datasets):
                    answer = self.prompt("unsaved changes - write them? [y/n/cancel]")
                    if answer.lower().startswith("y"):
                        self.save()
                    elif not answer.lower().startswith("n"):
                        continue
                return
            self.handle(key)

    def handle(self, key):
        body_height = max(self.stdscr.getmaxyx()[0] - 3, 1)
        if self.mode == self.ENTRIES:
            self._handle_entries(key, body_height)
        else:
            self._handle_tree(key, body_height)

    def _handle_common(self, key):
        if key == ord("e"):
            self.mode = self.ENTRIES if self.mode == self.TREE else self.TREE
        elif key == ord("\t"):
            self.dataset_index = (self.dataset_index + 1) % len(self.datasets)
            self.entry_cursor = self.entry_top = 0
            self.status = f"dataset: {self.dataset.name}"
        elif key == ord("w"):
            self.save()
        else:
            return False
        return True

    def _handle_entries(self, key, body_height):
        if self._handle_common(key):
            return
        if key in (curses.KEY_DOWN, ord("j")):
            self.entry_cursor += 1
        elif key in (curses.KEY_UP, ord("k")):
            self.entry_cursor -= 1
        elif key in (curses.KEY_NPAGE, 4):
            self.entry_cursor += body_height
        elif key in (curses.KEY_PPAGE, 21):
            self.entry_cursor -= body_height
        elif key in (curses.KEY_HOME, ord("g")):
            self.entry_cursor = 0
        elif key in (curses.KEY_END, ord("G")):
            self.entry_cursor = len(self.dataset.entries) - 1
        elif key in (ord("d"), curses.KEY_DC):
            self.remove_entry()

    def _handle_tree(self, key, body_height):
        if self._handle_common(key):
            return
        node = self.rows[self.cursor] if self.rows else None
        if key in (curses.KEY_DOWN, ord("j")):
            self.cursor += 1
        elif key in (curses.KEY_UP, ord("k")):
            self.cursor -= 1
        elif key in (curses.KEY_NPAGE, 4):
            self.cursor += body_height
        elif key in (curses.KEY_PPAGE, 21):
            self.cursor -= body_height
        elif key in (curses.KEY_HOME, ord("g")):
            self.cursor = 0
        elif key in (curses.KEY_END, ord("G")):
            self.cursor = len(self.rows) - 1
        elif key in (ord(" "), curses.KEY_ENTER, 10, 13):
            # One toggle key for whatever the row under the cursor has to
            # toggle: a directory's expanded state, a file's membership in
            # the dataset.
            if node and node.is_dir:
                self.toggle_dir(node)
            elif node:
                self.toggle_file(node)
        elif key in (curses.KEY_RIGHT, ord("l")):
            if node and node.is_dir and not node.expanded:
                self.tree.expand(node)
            elif node and node.is_dir:
                self.cursor += 1
        elif key in (curses.KEY_LEFT, ord("h")):
            if node and node.is_dir and node.expanded:
                node.expanded = False
            elif node and node.parent is not None and node.parent.depth >= 0:
                self.cursor = self.tree.visible().index(node.parent)
        elif key == ord("a"):
            self.commit_staged()
        elif ord("1") <= key <= ord("9") and node and not node.is_dir:
            self.assign_slot(node, key - ord("1"))
        elif key == ord("/"):
            self.filter = self.prompt("filter:").strip()
            self.search(self.cursor - 1, 1)
        elif key == ord("n"):
            self.search(self.cursor, 1)
        elif key == ord("N"):
            self.search(self.cursor, -1)


def load_datasets(only=None):
    names = sorted(n for n in os.listdir(DATASETS_DIR) if n.endswith("_hashes.json"))
    if only:
        name = only if only.endswith(".json") else f"{only}_hashes.json"
        if name not in names:
            raise SystemExit(f"no such dataset: {name} (have: {', '.join(names)})")
        names = [name] + [n for n in names if n != name]
    return [Dataset(os.path.join(DATASETS_DIR, name)) for name in names]


def load_catalog_hashes(app_id):
    """The committed catalog for app_id, or None if there isn't one yet -
    used only to warn about a pick tests would later reject (see
    test_dataset_hashes_are_in_catalog in tests/mtfw/test_*.py).
    """
    path = os.path.join(DATASETS_DIR, f"{app_id}_catalog.json")
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return {entry["path_hash"] for entry in json.load(f)}


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("app_id")
    parser.add_argument("game_root")
    parser.add_argument(
        "-d", "--dataset", default=None,
        help="Dataset to start on, e.g. mod_parsing (tab cycles through the rest)",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.game_root):
        raise SystemExit(f"game root does not exist: {args.game_root!r}")

    datasets = load_datasets(args.dataset)
    catalog_hashes = load_catalog_hashes(args.app_id)
    if catalog_hashes is None:
        print(f"note: no {args.app_id}_catalog.json - picks won't be catalog-checked")

    # Mounting a full install scans every .arc, which takes a while and
    # prints nothing once curses owns the screen.
    print(f"mounting {args.game_root} ...", flush=True)
    game_fs = MTFW_FS(args.game_root)

    curses.wrapper(lambda stdscr: App(
        stdscr, args.app_id, game_fs, datasets, catalog_hashes).run())


if __name__ == "__main__":
    main()
