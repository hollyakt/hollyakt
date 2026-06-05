"""Tests for the README projects-table generator."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_readme as br  # noqa: E402


SAMPLE = [
    {"emoji": "🧠", "name": "Foo", "url": "https://example.com/foo",
     "description": "does foo", "tech": "Python"},
]


def test_load_projects_matches_readme_entries():
    projects = br.load_projects()
    assert len(projects) >= 1
    for p in projects:
        assert {"emoji", "name", "url", "description", "tech"} <= p.keys()


def test_render_table_has_header_and_rows():
    table = br.render_table(SAMPLE)
    lines = table.splitlines()
    assert lines[0].startswith("| Project")
    assert lines[1].startswith("|---")
    assert "[**Foo**](https://example.com/foo)" in lines[2]
    assert "does foo" in lines[2] and "Python" in lines[2]


def test_inject_replaces_between_markers():
    readme = f"intro\n{br.START}\nOLD\n{br.END}\noutro\n"
    out = br.inject(readme, "NEW")
    assert "OLD" not in out
    assert f"{br.START}\nNEW\n{br.END}" in out
    assert out.startswith("intro") and out.rstrip().endswith("outro")


def test_inject_requires_markers():
    with pytest.raises(ValueError):
        br.inject("no markers here", "NEW")


def test_repo_readme_is_in_sync():
    """The committed README must match what the generator produces."""
    table = br.render_table(br.load_projects())
    current = br.README.read_text()
    assert br.inject(current, table) == current
