"""
Parser for the insight-outline DSL: a plain-text file naming which chart PNG
goes under which finding, so an xlsx builder (see build.py) can place them
without a one-off per-session driver script.

Format (see viz-rep's .claude/skills/insight-draft/SKILL.md for the full
spec and worked example):

    - <finding headline>
        ○ <repo-relative/path/to/chart.png>
        ○ <path/to/left.png> | <path/to/right.png>
        ○ BLANK

- A line starting with "- " begins a new finding (Section).
- An indented "    ○ " line under a finding is one row of chart image(s)
  belonging to it. "|" splits a row into side-by-side columns.
- A cell containing "BLANK" (case-insensitive) means no image there — the
  xlsx builder renders an italic "[Chart to insert: ...]" placeholder.
- Any other cell is a path, resolved against `repo_root`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_BULLET_RE = re.compile(r"^-\s+(.+)$")
_IMAGE_ROW_RE = re.compile(r"^\s+○\s+(.+)$")


class OutlineParseError(ValueError):
    """Malformed outline text, or an image path that doesn't resolve to a real file."""


@dataclass
class Section:
    headline: str
    rows: list[list[Path | None]] = field(default_factory=list)
    line_no: int = 0


def _resolve_cell(raw: str, *, repo_root: Path, validate_exists: bool, line_no: int) -> Path | None:
    cell = raw.strip()
    if cell.upper() == "BLANK":
        return None
    path = (repo_root / cell).resolve()
    if validate_exists and not path.is_file():
        raise OutlineParseError(f"line {line_no}: image not found: {path}")
    return path


def parse_outline(text: str, *, repo_root: Path, validate_exists: bool = True) -> list[Section]:
    """Parse outline DSL text into Section objects, resolving every non-BLANK
    image path against repo_root immediately, so build.py never touches paths."""
    sections: list[Section] = []
    current: Section | None = None

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue

        image_match = _IMAGE_ROW_RE.match(raw_line)
        if image_match:
            if current is None:
                raise OutlineParseError(f"line {line_no}: image row before any '- ' finding")
            cells = [
                _resolve_cell(cell, repo_root=repo_root, validate_exists=validate_exists, line_no=line_no)
                for cell in image_match.group(1).split("|")
            ]
            current.rows.append(cells)
            continue

        bullet_match = _BULLET_RE.match(raw_line)
        if bullet_match:
            current = Section(headline=bullet_match.group(1).strip(), line_no=line_no)
            sections.append(current)
            continue

        raise OutlineParseError(f"line {line_no}: unrecognized line: {raw_line!r}")

    return sections


def parse_outline_file(path: str | Path, *, repo_root: Path, validate_exists: bool = True) -> list[Section]:
    """Read `path`, delegate to parse_outline()."""
    text = Path(path).read_text(encoding="utf-8")
    return parse_outline(text, repo_root=repo_root, validate_exists=validate_exists)
