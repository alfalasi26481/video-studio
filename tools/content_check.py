"""Content rules for the channel: no organisations, no work/office topics, MSA not Gulf dialect.

Every check returns a list of Finding(code, message, text). The episode validator
calls these on every narration and on-screen string; they can also run alone:

    python3 tools/content_check.py "some text"
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass

# Product names that are allowed (the channel teaches Claude).
ALLOWED_BRANDS = {
    "claude", "anthropic", "claude code", "claude.ai", "cowork", "opus", "sonnet", "haiku",
}

# Organisation markers. Arabic: a generic noun that introduces a named entity.
# English: words that name an organisation or a sector.
AR_ORG_TERMS = [
    "وزارة", "وزارات", "هيئة", "مؤسسة", "شركة", "شركات", "بنك", "مصرف", "بلدية", "دائرة",
    "جامعة", "حكومة", "حكومي", "حكومية", "القيادة العامة", "مجلس", "جيش", "شرطة",
    "مستشفى", "سفارة", "مطار", "منظمة",
]
EN_ORG_TERMS = [
    "ministry", "authority", "government", "governmental", "municipality", "company",
    "corporation", "corp", "inc", "llc", "ltd", "bank", "airline", "airlines", "army",
    "military", "police", "embassy", "airport", "university", "council", "federation",
    "agency", "department", "hospital",
]
# Named brands/organisations that must never appear (other AI vendors, big tech, etc.).
EN_NAMED_ORGS = [
    "openai", "chatgpt", "google", "gemini", "microsoft", "copilot", "meta", "facebook",
    "apple", "amazon", "tesla", "nvidia", "deepseek", "grok", "xai", "emirates", "etihad",
    "adnoc", "aramco", "dewa", "rta",
]
AR_NAMED_ORGS = ["جوجل", "قوقل", "مايكروسوفت", "أبل", "آبل", "أمازون", "ميتا", "طيران الإمارات", "الاتحاد للطيران"]

# Work / office topics are out of scope for the channel.
AR_WORK_TERMS = [
    "مكتب", "المكتب", "دوام", "الدوام", "مديرك", "المدير", "مديري", "زملاء العمل", "زميلك في العمل",
    "وظيفة", "وظيفتك", "الوظيفة", "موظف", "موظفين", "اجتماع", "اجتماعات", "بريد العمل", "مقر العمل",
    "ترقية", "راتب", "العمل الرسمي",
]
EN_WORK_TERMS = [
    "office", "workplace", "boss", "manager", "coworker", "co-worker", "colleague", "colleagues",
    "employee", "employees", "employer", "meeting", "meetings", "your job", "salary", "promotion",
    "work email", "at work",
]

# Common Gulf-dialect words; the channel speaks Modern Standard Arabic.
GULF_DIALECT = [
    "شلون", "وايد", "الحين", "هالحين", "هالشي", "ابغى", "أبغى", "تبي", "يبي",
    "شو", "ليش", "عشان", "علشان", "مب", "مو", "وش", "جذي", "يالله", "خلاص", "اشوف", "هني",
]
# Deliberately absent (valid MSA too): أبي (my father), ترى (to see), كذا, زين (a name).


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    text: str


# Arabic letters + diacritics only — NOT punctuation (؟ ، ؛ are in U+0600–U+06FF too).
_L = r"\u0621-\u063A\u0640-\u065F\u0670-\u06D3\u06FA-\u06FF"

_AR_PREFIXES = "(?:و|ف|ب|ل|ك|ال|وال|بال|لل|فال|كال)?"


def _ar_exact_re(term: str) -> re.Pattern:
    # Dialect words: whole word only (optional و/ف), so «الخلاصة» never matches «خلاص».
    return re.compile(rf"(?<![{_L}])(?:و|ف)?{re.escape(term)}(?![{_L}])")


def _ar_word_re(term: str) -> re.Pattern:
    # Arabic has no \b for letters in every engine; bound by non-letter or string edge.
    t = re.escape(term)
    if term.startswith("ال"):
        prefix = "(?:و|ف|ب|ل|ك)?"
    else:
        prefix = _AR_PREFIXES
    return re.compile(rf"(?<![{_L}]){prefix}{t}(?:ها|هم|ات|ة|ي|ك|نا)?(?![{_L}])")


def _en_word_re(term: str) -> re.Pattern:
    return re.compile(rf"(?<![A-Za-z]){re.escape(term)}(?:s|es)?(?![A-Za-z])", re.IGNORECASE)


_COMPILED = {
    "org": [(t, _ar_word_re(t)) for t in AR_ORG_TERMS + AR_NAMED_ORGS]
    + [(t, _en_word_re(t)) for t in EN_ORG_TERMS + EN_NAMED_ORGS],
    "work": [(t, _ar_word_re(t)) for t in AR_WORK_TERMS] + [(t, _en_word_re(t)) for t in EN_WORK_TERMS],
    "dialect": [(t, _ar_exact_re(t)) for t in GULF_DIALECT],
}


def check_organisations(text: str) -> list[Finding]:
    out = []
    for term, rx in _COMPILED["org"]:
        if rx.search(text):
            out.append(Finding("ORG", f"اسم أو وصف جهة ممنوع: «{term}»", text))
    return out


def check_work_topics(text: str) -> list[Finding]:
    out = []
    for term, rx in _COMPILED["work"]:
        if rx.search(text):
            out.append(Finding("WORK", f"موضوع عمل/مكتب ممنوع: «{term}»", text))
    return out


def check_dialect(text: str) -> list[Finding]:
    out = []
    for term, rx in _COMPILED["dialect"]:
        if rx.search(text):
            out.append(Finding("DIALECT", f"كلمة لهجة خليجية، استخدم الفصحى: «{term}»", text))
    if "چ" in text or "ڤ" in text:
        out.append(Finding("DIALECT", "حرف غير فصيح (چ/ڤ)", text))
    return out


def check_text(text: str, lang: str) -> list[Finding]:
    findings = check_organisations(text) + check_work_topics(text)
    if lang == "ar":
        findings += check_dialect(text)
    return findings


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: content_check.py <text> [ar|en]")
        return 2
    text = argv[1]
    lang = argv[2] if len(argv) > 2 else ("ar" if re.search(r"[؀-ۿ]", text) else "en")
    found = check_text(text, lang)
    for f in found:
        print(f"[{f.code}] {f.message}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
