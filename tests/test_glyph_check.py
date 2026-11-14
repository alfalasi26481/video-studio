import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
pytest.importorskip("brotli")
import glyph_check as gc  # noqa: E402

REAL = gc.ROOT


@pytest.fixture
def root(tmp_path):
    """A fake master-claude/ with the real fonts + fonts.ts and empty episodes."""
    (tmp_path / "src" / "engine").mkdir(parents=True)
    (tmp_path / "src" / "episodes").mkdir(parents=True)
    shutil.copy(REAL / "src" / "engine" / "fonts.ts", tmp_path / "src" / "engine" / "fonts.ts")
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "fonts").symlink_to(REAL / "public" / "fonts")
    return tmp_path


def write_ts(root, body, nn="99"):
    (root / "src" / "episodes" / f"ep{nn}.ts").write_text(body, encoding="utf-8")


def test_parse_ranges():
    assert gc.parse_ranges("U+0600-06FF, U+200C, ") == [(0x600, 0x6FF), (0x200C, 0x200C)]
    with pytest.raises(ValueError):
        gc.parse_ranges("0600-06FF")


def test_real_unicode_ranges_load():
    ur = gc.load_unicode_ranges()
    for w in gc.WEIGHTS:
        assert f"Tajawal-{w}-arabic.woff2" in ur and f"Inter-{w}-latin.woff2" in ur


def test_approved_episodes_are_fully_covered():
    for nn in gc.all_episode_ids():
        assert gc.check_episode(nn) == [], nn


def test_arabic_and_latin_covered(root):
    cov = gc.Coverage(root)
    for ch in "توقف؟،«»Claude 5":
        assert ch.isspace() or cov.covered(ch, "Tajawal"), ch
    for ch in "STOP! «Claude» 5 — 'x'":
        assert ch.isspace() or cov.covered(ch, "Inter"), ch


def test_left_arrow_outside_unicode_range_is_flagged(root):
    # U+2190 is not in the latin subset's unicode-range (only 2191/2193 are)
    write_ts(root, "export const EP99_AR = {\n  text: {stop: 'السؤال ← الجواب'},\n};\n")
    miss = gc.check_episode("99", root)
    assert [m.codepoint for m in miss] == ["U+2190"]
    assert miss[0].lang == "ar"


def test_emoji_flagged_in_both_languages(root):
    write_ts(root, "export const EP99_AR = {\n  a: 'احفظ 🔥',\n};\nexport const EP99_EN = {\n  a: 'Save 🔥',\n};\n")
    miss = gc.check_episode("99", root)
    assert sorted(m.lang for m in miss) == ["ar", "en"]
    assert {m.char for m in miss} == {"🔥"}


def test_arabic_inside_english_composition_is_flagged(root):
    # Inter has no Arabic glyphs: Arabic text in an _EN const would fall back
    write_ts(root, "const Q_EN = [\n  {label: 'Hello مرحبا'},\n];\n")
    miss = gc.check_episode("99", root)
    assert miss and all(m.lang == "en" for m in miss)
    assert "م" in {m.char for m in miss}


def test_invisible_controls_skipped(root):
    write_ts(root, "export const EP99_AR = {\n  a: 'لـ‌Claude‏',\n};\n")
    assert gc.check_episode("99", root) == []


def test_caption_words_checked_with_their_language(root):
    words = [{"start": 0, "end": 1, "words": [[0.0, "تابعنا"], [0.5, "✨"]]}]
    (root / "src" / "episodes" / "ep99_words_ar.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    miss = gc.check_episode("99", root)
    assert [(m.source, m.char) for m in miss] == [("ep99_words_ar.json", "✨")]


def test_duplicates_reported_once(root):
    write_ts(root, "export const EP99_EN = {\n  a: '→ one',\n  b: '→ two',\n};\n")
    assert len(gc.check_episode("99", root)) == 1


def test_main_exit_codes(root, capsys):
    assert gc.main(["glyph_check", "01", "02"]) == 0
    write_ts(root, "export const EP99_EN = {\n  a: 'ok ✓',\n};\n")
    assert gc.main(["glyph_check"], root) == 1
    assert "U+2713" in capsys.readouterr().out
