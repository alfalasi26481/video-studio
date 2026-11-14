import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import script_length as sl  # noqa: E402

RATES = {"ar": 2.0, "en": 2.5}


def md(ar: str, en: str) -> str:
    return f"# x\n\n## السكربت — عربي (نص النطق)\n\n```\n{ar}\n```\n\n## Script — English (spoken)\n\n```\n{en}\n```\n\n## تعليق النشر\n\n```\nlots of other words here that must not count\n```\n"


def test_extracts_only_spoken_blocks():
    s = sl.spoken_scripts(md("كلمة " * 3, "word " * 4))
    assert sl.word_count(s["ar"]) == 3
    assert sl.word_count(s["en"]) == 4


def test_word_count_keeps_contractions_and_arabic():
    assert sl.word_count("You're prompting Claude.") == 3
    assert sl.word_count("توقف! أنت تكتب لـ كلود") == 5


def test_in_range_passes():
    est, f = sl.check({"ar": "و " * 60, "en": "w " * 75}, RATES)
    assert est == {"ar": 30.0, "en": 30.0}
    assert f == []


def test_too_long_and_too_short_are_errors():
    _, f = sl.check({"ar": "و " * 80, "en": "w " * 50}, RATES)
    msgs = [x.message for x in f if x.level == "error"]
    assert any("AR" in m and "longer" in m for m in msgs)
    assert any("EN" in m and "shorter" in m for m in msgs)


def test_parity_warning():
    _, f = sl.check({"ar": "و " * 52, "en": "w " * 85}, RATES)  # 26s vs 34s
    assert [x.level for x in f] == ["warning"]


def test_missing_script_is_error():
    _, f = sl.check({"ar": "و " * 60}, RATES)
    assert any(x.level == "error" and "EN" in x.message for x in f)


def test_voice_durations_order_ar_then_en():
    ts = "export const EP01_AR = {voiceDur: 32.3,}\nexport const EP01_EN = {voiceDur: 30.25,}"
    assert sl.voice_durations(ts) == {"ar": 32.3, "en": 30.25}


def test_calibrate_from_files(tmp_path):
    (tmp_path / "episodes").mkdir()
    (tmp_path / "src" / "episodes").mkdir(parents=True)
    (tmp_path / "episodes" / "ep01.md").write_text(md("و " * 60, "w " * 60), encoding="utf-8")
    (tmp_path / "src" / "episodes" / "ep01.ts").write_text("voiceDur: 30\nvoiceDur: 20", encoding="utf-8")
    # a draft without .ts must not influence calibration
    (tmp_path / "episodes" / "ep02.md").write_text(md("و " * 999, "w " * 999), encoding="utf-8")
    r = sl.calibrate(tmp_path)
    assert r == {"ar": 2.0, "en": 3.0}


def test_calibrate_falls_back_to_defaults(tmp_path):
    (tmp_path / "episodes").mkdir()
    (tmp_path / "src" / "episodes").mkdir(parents=True)
    assert sl.calibrate(tmp_path) == sl.DEFAULT_RATE


def test_real_engine_episodes_pass():
    rates = sl.calibrate()
    for nn in ("01", "02", "03"):
        text = (sl.ROOT / "episodes" / f"ep{nn}.md").read_text(encoding="utf-8")
        _, f = sl.check(sl.spoken_scripts(text), rates)
        assert [x for x in f if x.level == "error"] == [], (nn, f)


def test_measured_durations_judged_directly():
    est, f = sl.check_durations({"ar": 32.3, "en": 30.25})
    assert f == []
    _, f = sl.check_durations({"ar": 36.0, "en": 30.0})
    assert [x.level for x in f] == ["error", "warning"]
