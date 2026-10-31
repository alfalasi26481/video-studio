import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from content_check import check_dialect, check_organisations, check_text, check_work_topics  # noqa: E402


@pytest.mark.parametrize("text", [
    "اسأل وزارة الصحة",
    "راجع البنك قبل السفر",
    "موقع الشركة الرسمي",
    "طيران الإمارات",
    "Ask the ministry first",
    "Try ChatGPT or Gemini",
    "Built by Google",
    "the bank's app",
])
def test_flags_organisations(text):
    assert check_organisations(text)


@pytest.mark.parametrize("text", [
    "اكتب رسالة لمديرك",
    "لخّص الاجتماع",
    "في الدوام",
    "Email your boss",
    "summarise the meeting",
    "at the office",
])
def test_flags_work_topics(text):
    assert check_work_topics(text)


@pytest.mark.parametrize("text", ["شلون أكتب الطلب؟", "وايد مفيد", "ليش الرد طويل", "الحين جرّب"])
def test_flags_gulf_dialect(text):
    assert check_dialect(text)


@pytest.mark.parametrize("text", [
    "الخلاصة: وضوح ثم سياق",       # contains «خلاص» inside a longer MSA word
    "هناك طريقة أسهل",
    "ترى النتيجة بجانب المحادثة",
    "أبي يحب الطبخ",
])
def test_msa_is_not_dialect(text):
    assert check_dialect(text) == []


@pytest.mark.parametrize("text,lang", [
    ("اكتب طلبك بوضوح لـ Claude", "ar"),
    ("Claude did a great job on the planner", "en"),
    ("Anthropic makes Claude", "en"),
    ("metadata and a homepage", "en"),
    ("بنكهة الليمون", "ar"),
])
def test_clean_text_passes(text, lang):
    assert check_text(text, lang) == []


def test_arabic_punctuation_does_not_hide_a_term():
    # ؟ ، ؛ live in the Arabic Unicode block; they must count as word boundaries.
    from content_check import check_text
    for text in ("هل تكتب لبنك؟", "وزارة، ثم", "في المكتب؛ ثم", "شلون؟"):
        assert check_text(text, "ar"), text
