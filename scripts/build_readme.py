"""
Generate the Featured Projects table in README.md from data/projects.json.

The table between the PROJECTS markers is generated from a single source of
truth so the profile stays consistent and easy to update.

Usage:
    python scripts/build_readme.py          # rewrite README.md in place
    python scripts/build_readme.py --check   # exit 1 if README is out of sync
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DATA = ROOT / "data" / "projects.json"

START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"


def load_projects(path: Path = DATA) -> list:
    return json.loads(path.read_text())


def render_table(projects: list) -> str:
    """Render the projects list as a GitHub-flavoured markdown table."""
    lines = [
        "| Project | Description | Tech |",
        "|---------|-------------|------|",
    ]
    for p in projects:
        link = f"[**{p['name']}**]({p['url']})"
        lines.append(f"| {p['emoji']} {link} | {p['description']} | {p['tech']} |")
    return "\n".join(lines)


def inject(readme_text: str, table: str) -> str:
    """Replace the content between the PROJECTS markers with the table."""
    if START not in readme_text or END not in readme_text:
        raise ValueError(f"README is missing {START} / {END} markers")
    pre, rest = readme_text.split(START, 1)
    _, post = rest.split(END, 1)
    return f"{pre}{START}\n{table}\n{END}{post}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Exit non-zero if README is out of sync.")
    args = parser.parse_args()

    table = render_table(load_projects())
    current = README.read_text()
    updated = inject(current, table)

    if args.check:
        if current != updated:
            print("README.md is out of sync with data/projects.json. "
                  "Run: python scripts/build_readme.py")
            return 1
        print("README.md is in sync.")
        return 0

    README.write_text(updated)
    print("README.md updated from data/projects.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
