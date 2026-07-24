"""outline.py: parses the finding/image-row DSL into Section objects."""

from pathlib import Path

import pytest

from src.report.outline import OutlineParseError, Section, parse_outline

EXAMPLE_DOC = """\
- Overview of active PCB client
    ○ quest_1/quest1_multi_ax.png
    ○ quest_1_xsel/quest_1_xsel.png
- Multi-lenders, especially with BANK, are significantly more Digital
    ○ quest_2_1/quest2_1.png | BLANK
    ○ quest_2_2/quest2_2_1.png | quest_2_2/quest2_2_2.png
    ○ quest_2_3/quest2_3_1.png | quest_2_3/quest2_3_2.png
- This behavior can be explained by two hypotheses:
    ○ BLANK
"""


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


@pytest.fixture
def repo_root(tmp_path):
    for rel in [
        "quest_1/quest1_multi_ax.png",
        "quest_1_xsel/quest_1_xsel.png",
        "quest_2_1/quest2_1.png",
        "quest_2_2/quest2_2_1.png",
        "quest_2_2/quest2_2_2.png",
        "quest_2_3/quest2_3_1.png",
        "quest_2_3/quest2_3_2.png",
    ]:
        _touch(tmp_path / rel)
    return tmp_path


def test_parses_example_doc_into_three_sections(repo_root):
    sections = parse_outline(EXAMPLE_DOC, repo_root=repo_root)
    assert [s.headline for s in sections] == [
        "Overview of active PCB client",
        "Multi-lenders, especially with BANK, are significantly more Digital",
        "This behavior can be explained by two hypotheses:",
    ]
    assert len(sections[0].rows) == 2
    assert len(sections[1].rows) == 3
    assert len(sections[2].rows) == 1


def test_split_row_resolves_real_path_and_blank_to_none(repo_root):
    sections = parse_outline(EXAMPLE_DOC, repo_root=repo_root)
    row = sections[1].rows[0]  # "quest_2_1.png | BLANK"
    assert row[0] == (repo_root / "quest_2_1/quest2_1.png").resolve()
    assert row[1] is None


def test_bare_blank_row_is_single_none_cell(repo_root):
    sections = parse_outline(EXAMPLE_DOC, repo_root=repo_root)
    assert sections[2].rows[0] == [None]


def test_finding_with_no_image_rows_is_valid(repo_root):
    sections = parse_outline("- Text-only finding\n", repo_root=repo_root)
    assert sections == [Section(headline="Text-only finding", rows=[], line_no=1)]


def test_image_row_before_any_bullet_raises(repo_root):
    with pytest.raises(OutlineParseError):
        parse_outline("    ○ quest_1/quest1_multi_ax.png\n", repo_root=repo_root)


def test_unrecognized_line_raises(repo_root):
    with pytest.raises(OutlineParseError):
        parse_outline("- Finding\nnot a bullet or image row\n", repo_root=repo_root)


def test_missing_image_raises_when_validate_exists(tmp_path):
    with pytest.raises(OutlineParseError):
        parse_outline("- Finding\n    ○ does/not/exist.png\n", repo_root=tmp_path)


def test_missing_image_allowed_when_validate_exists_false(tmp_path):
    sections = parse_outline(
        "- Finding\n    ○ does/not/exist.png\n", repo_root=tmp_path, validate_exists=False
    )
    assert sections[0].rows[0][0] == (tmp_path / "does/not/exist.png").resolve()
