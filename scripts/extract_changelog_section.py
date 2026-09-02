#!/usr/bin/env python3
"""
Print CHANGELOG.md's section for a given version, for use as GitHub Release
notes on a tagged release.

Usage:
    python scripts/extract_changelog_section.py 0.5.0

Expects Keep a Changelog format (https://keepachangelog.com/): a line like
"## [0.5.0] - 2026-04-03" starting the section, running until the next "## ["
heading or end of file. Exits non-zero with a clear message if no matching
section exists - a missing section means CHANGELOG.md wasn't updated before
tagging, not something to silently paper over with empty release notes.
"""
import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"


def extract_section(changelog_text, version):
    pattern = re.compile(
        r"^## \[" + re.escape(version) + r"\][^\n]*\n(.*?)(?=^## \[|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(changelog_text)
    if not match:
        return None
    return match.group(1).strip()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("version", help='Version to extract, e.g. "0.5.0" (no "v" prefix)')
    args = parser.parse_args()

    section = extract_section(CHANGELOG_PATH.read_text(), args.version)
    if section is None:
        raise SystemExit(
            f'No "## [{args.version}]" section found in {CHANGELOG_PATH} - '
            "update the changelog before tagging a release"
        )
    print(section)


if __name__ == "__main__":
    main()
