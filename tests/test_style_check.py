import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import style_check as st  # noqa: E402
import script_length as sl  # noqa: E402

S = st.Style


def test_md_line_parsed():
    line = "- الأسلوب (`docs/STYLE_PLAN.md`): ثيم `gold` (ذهبي) · افتتاحية `reveal` · كسر نمط `snap`."
    assert st.style_from_md(f"# t\n{line}\n") == S("gold", "reveal", "snap")


def test_md_without_style_is_none():
    assert st.style_from_md("# t\n- الحالة: مسودة\n") is None
    assert st.style_from_md("- الأسلوب: ثيم `purple` · افتتاحية `reveal`") is None


def test_ts_style_parsed():
    ts = "const style: Style = {theme: 'electric', hook: 'question', breaks: 'snap', gradeExcept: [clips.hook]};"
    assert st.style_from_ts(ts) == S("electric", "question", "snap")


def test_repeat_of_previous_theme_or_hook_is_error():
    styles = {6: S("electric", "question", "snap"), 7: S("electric", "question", "snap")}
    errors, _ = st.check(styles, {}, {})
    assert len(errors) == 2 and all(e.startswith("EP07") for e in errors)


def test_ts_md_mismatch_is_error_plan_mismatch_is_warning():
    styles = {7: S("gold", "reveal", "snap")}
    errors, warnings = st.check(styles, {7: S("mint", "reveal", "snap")}, {7: S("gold", "stop", "snap")})
    assert len(errors) == 1 and "epNN.ts" in errors[0]
    assert len(warnings) == 1


def test_missing_style_line_is_error():
    errors, _ = st.check({8: None}, {}, {})
    assert errors and errors[0].startswith("EP08")


def test_plan_table_parsed():
    t = "| الحلقة | الثيم |\n|---|---|\n| 06 ✅ (1 نوفمبر) | electric | question | snap |\n| 07 | gold | reveal | snap |\n"
    assert st.plan_table(t) == {6: S("electric", "question", "snap"), 7: S("gold", "reveal", "snap")}


def test_real_episodes_pass():
    _, errors, _ = st.load()
    assert errors == []


def test_every_real_script_within_length():
    rates = sl.calibrate()
    files = sorted((sl.ROOT / "episodes").glob("ep[0-9][0-9].md"))
    assert len(files) >= 7
    for p in files:
        _, f = sl.check(sl.spoken_scripts(p.read_text(encoding="utf-8")), rates)
        assert [x for x in f if x.level == "error"] == [], (p.name, f)
