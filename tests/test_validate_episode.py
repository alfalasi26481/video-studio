import copy
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from validate_episode import episode_files, validate_data, validate_file  # noqa: E402


def _scene(role, motion="KineticTitle", **extra):
    ar = {"narration": "هذه جملة عربية قصيرة للتجربة فقط", "on_screen": "عنوان قصير"}
    en = {"narration": "This is a short English test sentence", "on_screen": "Short title"}
    ar.update(extra.get("ar", {}))
    en.update(extra.get("en", {}))
    return {"role": role, "motion": motion, "ar": ar, "en": en}


def good():
    long_ar = " ".join(["كلمة"] * 30)
    long_en = " ".join(["word"] * 30)
    return {
        "id": "ep99",
        "level": "beginner",
        "title": {"ar": "حلقة تجريبية", "en": "Test episode"},
        "sources": [{"url": "https://support.claude.com/en/articles/1", "claim": "x", "checked": "2026-10-30"}],
        "scenes": [
            _scene("hook"),
            _scene("step", "BoxReveal", ar={"narration": long_ar, "items": ["أ", "ب"]},
                   en={"narration": long_en, "items": ["A", "B"]}),
            _scene("step", "ChatMock", ar={"narration": long_ar, "chat": {"user": "سؤال", "reply": "جواب"}},
                   en={"narration": long_en, "chat": {"user": "Q", "reply": "A"}}),
            _scene("recap", "FlowDiagram", ar={"items": ["أ", "ب"]}, en={"items": ["A", "B"]}),
            _scene("cta", "Arrow"),
        ],
    }


def errs(data):
    return validate_data(data).errors


def test_good_episode_is_valid():
    r = validate_data(good())
    assert r.ok, r.errors
    assert r.est_seconds["ar"] > 0


def test_every_scene_needs_both_languages():
    d = good()
    del d["scenes"][1]["en"]
    assert any("مفقود" in e for e in errs(d))


def test_structure_hook_first_cta_last_recap_before_cta():
    d = good()
    d["scenes"][0], d["scenes"][-1] = d["scenes"][-1], d["scenes"][0]
    e = errs(d)
    assert any("hook" in x for x in e) and any("cta" in x for x in e)

    d = good()
    d["scenes"].insert(3, d["scenes"].pop(1))  # step between recap and cta
    assert any("recap" in x for x in errs(d))


def test_motion_must_be_a_known_component():
    d = good()
    d["scenes"][1]["motion"] = "StaticSlide"
    assert any("motion" in x for x in errs(d))


def test_chatmock_needs_chat_and_boxes_need_items():
    d = good()
    del d["scenes"][2]["ar"]["chat"]
    assert any("ChatMock" in x for x in errs(d))
    d = good()
    d["scenes"][1]["en"]["items"] = ["only one"]
    assert any("items" in x for x in errs(d))


def test_items_count_must_match_across_languages():
    d = good()
    d["scenes"][1]["en"]["items"] = ["A", "B", "C"]
    assert any("يختلف" in x for x in errs(d))


def test_sources_must_be_official_anthropic_pages():
    d = good()
    d["sources"] = []
    assert errs(d)
    d = good()
    d["sources"][0]["url"] = "https://example.com/claude-tips"
    assert any("رسمي" in x for x in errs(d))


def test_language_scripts_are_checked():
    d = good()
    d["scenes"][0]["ar"]["narration"] = "This is not Arabic at all here"
    d["scenes"][0]["en"]["on_screen"] = "عنوان"
    e = errs(d)
    assert any("حروفاً عربية" in x for x in e) and any("Arabic letters" in x for x in e)


def test_content_rules_are_enforced_in_scenes():
    d = good()
    d["scenes"][0]["ar"]["narration"] = "اكتب رسالة لمديرك عن الاجتماع القادم بسرعة"
    d["scenes"][0]["en"]["narration"] = "Ask Google or the ministry for the answer"
    e = errs(d)
    assert any("[WORK]" in x for x in e) and any("[ORG]" in x for x in e)


def test_word_limits():
    d = good()
    d["scenes"][0]["ar"]["on_screen"] = " ".join(["كلمة"] * 11)
    d["scenes"][0]["en"]["narration"] = "Too short"
    e = errs(d)
    assert any("on_screen" in x for x in e) and any("narration" in x for x in e)


@pytest.mark.parametrize("bad", [None, [], "text", {"id": "x"}])
def test_garbage_input_does_not_crash(bad):
    assert not validate_data(bad).ok


def test_filename_must_match_id(tmp_path):
    p = tmp_path / "ep01.yaml"
    p.write_text(yaml.safe_dump(good(), allow_unicode=True), encoding="utf-8")
    assert any("اسم الملف" in e for e in validate_file(p).errors)


@pytest.mark.parametrize("path", episode_files(), ids=lambda p: p.name)
def test_repo_episodes_are_valid(path):
    r = validate_file(path)
    assert r.ok, r.errors


def test_repo_has_three_samples_and_backlog():
    assert len(episode_files()) >= 3
    backlog = yaml.safe_load((ROOT / "episodes" / "backlog.yaml").read_text(encoding="utf-8"))
    ids = [e["id"] for e in backlog["episodes"]]
    assert len(ids) == len(set(ids))
    for f in episode_files():
        assert f.stem in ids, f"{f.stem} missing from backlog"
