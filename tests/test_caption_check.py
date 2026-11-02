import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import caption_check as cc  # noqa: E402


def lines(*tokens):
    return [{"start": 0, "end": 1, "words": [[i * 0.1, t] for i, t in enumerate(tokens)]}]


def test_glued_prefix_is_flagged():
    assert cc.mixed_tokens(lines("قل", "لـClaude:")) == [(0.1, "لـClaude:")]


def test_separate_tokens_pass():
    assert cc.mixed_tokens(lines("قل", "لـ", "Claude:")) == []


def test_pure_latin_and_pure_arabic_pass():
    assert cc.mixed_tokens(lines("Claude", "مهارة،", "3")) == []


def test_new_episode_error_legacy_warning(tmp_path, monkeypatch):
    monkeypatch.setattr(cc, "ROOT", tmp_path)
    for nn in ("04", "12"):
        (tmp_path / f"ep{nn}_words_ar.json").write_text(json.dumps(lines("لـClaude")), encoding="utf-8")
    assert cc.check(["04"]) == (0, 1)
    assert cc.check(["12"]) == (1, 0)
    assert cc.main(["12"]) == 1
    assert cc.main(["04"]) == 0


def test_repo_episodes_have_no_errors():
    errors, _ = cc.check(sorted(p.name[2:4] for p in cc.ROOT.glob("ep*_words_ar.json")))
    assert errors == 0


def test_arabic_punctuation_after_latin_passes():
    assert cc.mixed_tokens(lines("Claude،", "Claude؟")) == []


def test_two_latin_tokens_in_arabic_line_flagged():
    assert cc.latin_runs(lines("الحل:", "Claude", "Code")) == [(0.1, "Claude Code")]


def test_nbsp_joined_latin_passes():
    assert cc.latin_runs(lines("الحل:", "Claude\u00a0Code")) == []
    assert cc.latin_runs(lines("تبويب", "Code", "ثم")) == []


def test_ar_field_with_two_latin_words_flagged():
    ts = ("const STEPS_AR = [{label: 'x', ex: 'Claude Code'}];\nconst STEPS_EN = [{ex: 'Open Code now'}];\n"
          "export const EP99_AR: EpisodeDataV2 = {text: {formulaTitle: 'Claude Code', hookSub: 'صفحة بلا كود'}};\n"
          "export const EP99_EN: EpisodeDataV2 = {text: {formulaTitle: 'Claude Code'}};")
    assert cc.ar_field_runs(ts) == ["Claude Code", "Claude Code"]
    ok = ts.replace("Claude Code", "Claude\u00a0Code")
    assert cc.ar_field_runs(ok) == []
