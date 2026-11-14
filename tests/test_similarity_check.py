import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import similarity_check as sc  # noqa: E402


def ep(nn, ar="", en="", sar=(), sen=()):
    return sc.Episode(nn, (ar, en), (list(sar), list(sen)))


def levels(found):
    return sorted(f.level for f in found)


def test_normalize_unifies_claude_and_arabic_forms():
    assert sc.normalize("كلود يكتب")[0] == "claude"
    assert sc.normalize("أمثلة") == sc.normalize("امثله")
    assert sc.normalize("doesn't") == ["doesnt"]


def test_shared_four_words_in_script_is_error():
    a = ep("20", en="You get a generic reply that sounds bland.")
    b = ep("21", en="Then a generic reply that sounds odd.")
    found = sc.compare(a, b)
    assert "error" in levels(found)
    assert any("generic reply that sounds" in f.text for f in found)


def test_three_words_is_warning_only():
    a = ep("20", en="Ask about it clearly now.")
    b = ep("21", en="Please ask about it later.")
    assert levels(sc.compare(a, b)) == ["warning"]


def test_series_signature_is_not_counted():
    sig = "Stop! The fix is simple. One: x. See the difference... Save this video and follow for more."
    assert sc.compare(ep("20", en=sig), ep("21", en=sig)) == []
    ar = "توقف! الحل بسيط. شاهد الفرق... احفظ الفيديو، وتابعنا لمهارة جديدة."
    assert sc.compare(ep("20", ar=ar), ep("21", ar=ar)) == []


def test_cta_sentence_is_stripped():
    assert sc.strip_cta("A b c. Save this video and follow") == "A b c. "


def test_near_identical_screen_text_is_error():
    found = sc.compare(ep("20", sar=["رد عام لا يشبهك"]), ep("21", sar=["كلام عام لا يشبهك"]))
    assert levels(found) == ["error"]


def test_short_labels_need_same_words():
    assert sc.compare(ep("20", sar=["محادثة جديدة"]), ep("21", sar=["محادثة خفية"])) == []
    assert levels(sc.compare(ep("20", sen=["Made for you"]), ep("21", sen=["Made for you"]))) == ["error"]


def test_legacy_pair_becomes_warning():
    a, b = ep("01", sen=["Made for you"]), ep("02", sen=["Made for you"])
    found = sc.compare(a, b)
    assert levels(found) == ["warning"] and "مقبول قديماً" in found[0].text


def test_new_episode_against_legacy_still_errors():
    found = sc.compare(ep("01", sen=["A generic reply"]), ep("10", sen=["A generic reply"]))
    assert levels(found) == ["error"]


def test_screen_from_ts_reads_fields_and_steps():
    ts = """
const STEPS_AR: Step[] = [
  {n: '1', label: 'الصق 3 أمثلة', ex: 'كتبتها أنت', color: C, icon: 'task'},
];
const STEPS_EN: Step[] = [
  {n: '1', label: 'Paste 3 examples', ex: "Your own", color: C, icon: 'task'},
];
export const EP10_AR = { text: { badLabel: 'كأن غريباً كتبها', after: 'بأسلوبك أنت', }, };
export const EP10_EN = { text: { badLabel: 'Like a stranger wrote it', after: 'Your style', }, };
"""
    ar, en = sc.screen_from_ts(ts)
    assert "كأن غريباً كتبها" in ar and "الصق 3 أمثلة" in ar and "بأسلوبك أنت" in ar
    assert "Like a stranger wrote it" in en and "Your own" in en


def test_screen_from_md_table():
    md = """## نصوص الشاشة

| الحقل | AR | EN |
|---|---|---|
| badLabel | رد طويل | Long answer |
| 1 | اسمك — أسفل اليسار | Initials — Bottom left |
| before / after | فقرة طويلة / 3 نقاط | Long paragraph / 3 bullets |
| daily | مهارة | Skill |

## اللقطات
"""
    ar, en = sc.screen_from_md(md)
    assert ar == ["رد طويل", "اسمك", "أسفل اليسار", "فقرة طويلة", "3 نقاط"]
    assert "Bottom left" in en and "Skill" not in en


def test_repository_has_no_errors():
    errors = [f for f in sc.run() if f.level == "error"]
    assert errors == [], "\n".join(map(str, errors))
