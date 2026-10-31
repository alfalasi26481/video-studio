"""Validate episodes/<id>.yaml against the channel's episode format.

    python3 tools/validate_episode.py episodes/ep101.yaml [...]
    python3 tools/validate_episode.py --all

Exit code 0 = every file valid. Errors block production; warnings do not.
See docs/EPISODE_FORMAT.md for the format.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_check import check_text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("ar", "en")
ROLES = ("hook", "step", "recap", "cta")
MOTIONS = ("KineticTitle", "BoxReveal", "Arrow", "FlowDiagram", "ChatMock")
LEVELS = ("beginner", "intermediate", "pro")
STATUSES = ("draft", "verified", "rendered")
OFFICIAL_HOSTS = {
    "anthropic.com", "www.anthropic.com", "claude.com", "www.claude.com", "claude.ai",
    "docs.claude.com", "platform.claude.com", "support.claude.com", "docs.anthropic.com",
    "support.anthropic.com", "code.claude.com",
}
ID_RE = re.compile(r"^ep\d{2,4}$")
ARABIC = re.compile(r"[؀-ۿ]")
LATIN_WORD = re.compile(r"[A-Za-z]+")
# Speaking rate used to estimate length before TTS exists (words per second).
WPS = {"ar": 2.2, "en": 2.6}
MAX_ON_SCREEN_WORDS = 10
NARRATION_WORDS = (4, 45)
TOTAL_SECONDS = (15, 90)


@dataclass
class Report:
    path: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    est_seconds: dict[str, float] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors


def _words(s: str) -> int:
    return len(s.split())


def _check_lang_text(rep: Report, where: str, lang: str, text: str) -> None:
    if lang == "ar" and not ARABIC.search(text):
        rep.errors.append(f"{where}: النص العربي لا يحتوي حروفاً عربية")
    if lang == "en" and ARABIC.search(text):
        rep.errors.append(f"{where}: English text contains Arabic letters")
    for f in check_text(text, lang):
        rep.errors.append(f"{where}: [{f.code}] {f.message}")


def validate_data(data: object, path: str = "<memory>") -> Report:
    rep = Report(path)
    if not isinstance(data, dict):
        rep.errors.append("الملف يجب أن يكون قاموساً (mapping) في المستوى الأعلى")
        return rep

    eid = data.get("id")
    if not isinstance(eid, str) or not ID_RE.match(eid):
        rep.errors.append(f"id غير صالح: {eid!r} (المطلوب مثل ep101)")
    elif path not in ("<memory>",) and Path(path).stem != eid:
        rep.errors.append(f"اسم الملف يجب أن يطابق id ({eid}.yaml)")

    if data.get("level") not in LEVELS:
        rep.errors.append(f"level يجب أن يكون أحد {LEVELS}")
    if data.get("status", "draft") not in STATUSES:
        rep.errors.append(f"status يجب أن يكون أحد {STATUSES}")

    title = data.get("title")
    if not isinstance(title, dict) or any(not isinstance(title.get(l), str) or not title.get(l).strip() for l in LANGS):
        rep.errors.append("title يحتاج ar و en")
    else:
        for l in LANGS:
            _check_lang_text(rep, f"title.{l}", l, title[l])

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        rep.errors.append("sources مطلوب: كل معلومة عن Claude تحتاج صفحة رسمية من Anthropic")
    else:
        for i, s in enumerate(sources):
            if not isinstance(s, dict) or not s.get("url") or not s.get("claim"):
                rep.errors.append(f"sources[{i}]: يحتاج url و claim")
                continue
            host = urlparse(str(s["url"])).hostname or ""
            if host not in OFFICIAL_HOSTS:
                rep.errors.append(f"sources[{i}]: {host or s['url']} ليس موقعاً رسمياً لـ Anthropic")
            if not s.get("checked"):
                rep.warnings.append(f"sources[{i}]: لا يوجد تاريخ تحقق (checked)")

    scenes = data.get("scenes")
    if not isinstance(scenes, list) or len(scenes) < 4:
        rep.errors.append("scenes يحتاج 4 مشاهد على الأقل: hook ثم steps ثم recap ثم cta")
        return rep

    roles = []
    seconds = {l: 0.0 for l in LANGS}
    for i, sc in enumerate(scenes):
        where = f"scenes[{i}]"
        if not isinstance(sc, dict):
            rep.errors.append(f"{where}: المشهد يجب أن يكون قاموساً")
            continue
        role = sc.get("role")
        roles.append(role)
        if role not in ROLES:
            rep.errors.append(f"{where}: role يجب أن يكون أحد {ROLES}")
        motion = sc.get("motion")
        if motion not in MOTIONS:
            rep.errors.append(f"{where}: motion يجب أن يكون أحد {MOTIONS} (لا شرائح نصية ثابتة)")
        for l in LANGS:
            t = sc.get(l)
            lw = f"{where}.{l}"
            if not isinstance(t, dict):
                rep.errors.append(f"{lw}: مفقود — كل مشهد له نسخة عربية وإنجليزية")
                continue
            nar, ons = t.get("narration"), t.get("on_screen")
            if not isinstance(nar, str) or not nar.strip():
                rep.errors.append(f"{lw}.narration: مفقود")
            else:
                n = _words(nar)
                if not NARRATION_WORDS[0] <= n <= NARRATION_WORDS[1]:
                    rep.errors.append(f"{lw}.narration: {n} كلمة (المسموح {NARRATION_WORDS[0]}–{NARRATION_WORDS[1]})")
                seconds[l] += n / WPS[l]
                _check_lang_text(rep, f"{lw}.narration", l, nar)
            if not isinstance(ons, str) or not ons.strip():
                rep.errors.append(f"{lw}.on_screen: مفقود")
            else:
                if _words(ons) > MAX_ON_SCREEN_WORDS:
                    rep.errors.append(f"{lw}.on_screen: أكثر من {MAX_ON_SCREEN_WORDS} كلمات")
                _check_lang_text(rep, f"{lw}.on_screen", l, ons)
            if motion == "ChatMock":
                chat = t.get("chat")
                if not isinstance(chat, dict) or not chat.get("user") or not chat.get("reply"):
                    rep.errors.append(f"{lw}.chat: ChatMock يحتاج user و reply")
                else:
                    for k in ("user", "reply"):
                        _check_lang_text(rep, f"{lw}.chat.{k}", l, str(chat[k]))
            if motion in ("BoxReveal", "FlowDiagram"):
                items = t.get("items")
                if not isinstance(items, list) or not 2 <= len(items) <= 5:
                    rep.errors.append(f"{lw}.items: {motion} يحتاج 2–5 عناصر")
                else:
                    for j, it in enumerate(items):
                        _check_lang_text(rep, f"{lw}.items[{j}]", l, str(it))
        ar_items, en_items = (sc.get("ar") or {}).get("items"), (sc.get("en") or {}).get("items")
        if isinstance(ar_items, list) and isinstance(en_items, list) and len(ar_items) != len(en_items):
            rep.errors.append(f"{where}: عدد العناصر يختلف بين ar و en")
        if i > 0 and isinstance(scenes[i - 1], dict) and scenes[i - 1].get("motion") == motion and motion == "KineticTitle":
            rep.warnings.append(f"{where}: مشهدان KineticTitle متتاليان — نوّع الحركة")

    if roles and roles[0] != "hook":
        rep.errors.append("أول مشهد يجب أن يكون hook")
    if roles and roles[-1] != "cta":
        rep.errors.append("آخر مشهد يجب أن يكون cta")
    if roles.count("hook") != 1 or roles.count("cta") != 1 or roles.count("recap") != 1:
        rep.errors.append("المطلوب hook واحد و recap واحد و cta واحد")
    if "step" not in roles:
        rep.errors.append("المطلوب مشهد step واحد على الأقل")
    if len(roles) >= 2 and roles[-2] != "recap":
        rep.errors.append("recap يأتي مباشرة قبل cta")

    for l in LANGS:
        rep.est_seconds[l] = round(seconds[l], 1)
        if not TOTAL_SECONDS[0] <= seconds[l] <= TOTAL_SECONDS[1]:
            rep.warnings.append(f"المدة التقديرية ({l}) {seconds[l]:.0f}ث خارج {TOTAL_SECONDS[0]}–{TOTAL_SECONDS[1]}ث")
    return rep


def validate_file(path: str | Path) -> Report:
    p = Path(path)
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        r = Report(str(p))
        r.errors.append(f"تعذّرت قراءة الملف: {e}")
        return r
    return validate_data(data, str(p))


def episode_files() -> list[Path]:
    return sorted(p for p in (ROOT / "episodes").glob("ep*.yaml"))


def main(argv: list[str]) -> int:
    paths = episode_files() if argv[1:] in ([], ["--all"]) else [Path(a) for a in argv[1:]]
    bad = 0
    for p in paths:
        r = validate_file(p)
        mark = "✓" if r.ok else "✗"
        print(f"{mark} {p.name}  ~{r.est_seconds.get('ar', 0)}s ar / ~{r.est_seconds.get('en', 0)}s en")
        for e in r.errors:
            print(f"   ERROR {e}")
        for w in r.warnings:
            print(f"   warn  {w}")
        bad += not r.ok
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
