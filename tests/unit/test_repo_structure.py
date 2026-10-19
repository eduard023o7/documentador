"""Monorepo rules: BR-U0-31 (content has no code) and RNF-10 (content imports nothing)."""

from ..conftest import ROOT

ALLOWED_SUFFIXES = {".md", ".yaml", ".docx"}
ALLOWED_NAMES = {".gitkeep"}


def test_content_has_only_markdown_yaml_and_word():
    content = ROOT / "contenido"
    offenders = [
        p.relative_to(ROOT).as_posix()
        for p in content.rglob("*")
        if p.is_file() and p.suffix not in ALLOWED_SUFFIXES and p.name not in ALLOWED_NAMES
    ]
    assert offenders == []


def test_content_is_not_executable():
    content = ROOT / "contenido"
    assert not [p for p in content.rglob("*") if p.is_file() and p.stat().st_mode & 0o111]
