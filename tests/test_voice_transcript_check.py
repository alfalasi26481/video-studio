import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import voice_transcript_check as vtc


def words(text, step=0.5):
    return [[round(i * step, 2), round(i * step + 0.4, 2), w] for i, w in enumerate(text.split())]


def test_normalize_arabic_forms_and_aliases():
    assert vtc.normalize("أعلى", "ar") == vtc.normalize("اعلي", "ar")
    assert vtc.normalize("ذاكرةُ", "ar") == "ذاكره"
    assert vtc.normalize("3", "ar") == vtc.normalize("ثلاثة", "ar")
    assert vtc.normalize("Claude", "ar") == "كلود"
    assert vtc.normalize("Claude's", "en") == vtc.normalize("Claudes", "en")
    assert vtc.normalize("2", "en") == "two"


def test_perfect_voice_has_full_recall():
    s = "الحل: ذاكرة كلود. واحد: قل تذكّر."
    rep = vtc.check(s, words("الحل ذاكرة Claude 1 قل تذكر"), "ar")
    assert rep.recall == 1.0 and rep.misses == []


def test_swapped_word_is_reported_with_time():
    # EP09-AR: «أعلى» heard as «على» — similar spelling still matches; a real swap is flagged
    s = "اضغط أيقونة الشبح في أعلى اليمين"
    rep = vtc.check(s, words("اضغط أيقونة الشبح في أسفل اليمين"), "ar")
    assert rep.matched == 5
    assert len(rep.misses) == 1
    m = rep.misses[0]
    assert m.words == "اعلي" and m.heard == "اسفل" and m.at == 2.0


def test_dropped_words_are_reported():
    s = "Save this video and follow for more"
    rep = vtc.check(s, words("Save this video for more"), "en")
    assert rep.matched == 5 and rep.total == 7
    assert rep.misses[0].words == "and follow" and rep.misses[0].heard == ""


def test_fuzzy_misspelling_counts_as_heard():
    rep = vtc.check("Claude's memory", words("Claud's memory"), "en")
    assert rep.recall == 1.0


def test_split_and_joined_words_count_as_heard():
    rep = vtc.check("شاهد الفرق", words("شاهدالفرق"), "ar")
    assert rep.recall == 1.0


def test_extra_heard_words_do_not_count_against():
    rep = vtc.check("one two three", words("um one two three thanks"), "en")
    assert rep.recall == 1.0


def _repo(tmp_path: Path, ar_script: str, with_wav=True) -> Path:
    root = tmp_path / "mc"
    (root / "episodes").mkdir(parents=True)
    (root / "public" / "vo").mkdir(parents=True)
    (root / "episodes" / "ep42.md").write_text(
        f"# x\n\n## السكربت — عربي (نص النطق)\n\n```\n{ar_script}\n```\n", encoding="utf-8")
    if with_wav:
        (root / "public" / "vo" / "ep42_ar.wav").write_bytes(b"")
    return root


def test_run_errors_below_min_recall(tmp_path, capsys):
    root = _repo(tmp_path, "واحد اثنان ثلاثة أربعة خمسة")
    code = vtc.run(["42"], ["ar"], root, heard=lambda nn, lang, r: words("واحد"))
    out = capsys.readouterr().out
    assert code == 1 and "[error] EP42-AR" in out and "listen at" in out


def test_run_ok_and_skips_missing_voice(tmp_path, capsys):
    root = _repo(tmp_path, "واحد اثنان")
    code = vtc.run(["42"], ["ar", "en"], root, heard=lambda nn, lang, r: words("واحد اثنين"))
    out = capsys.readouterr().out
    assert code == 0 and "[ok] EP42-AR" in out and "EP42-EN: skipped" in out


def test_episodes_with_voice(tmp_path):
    root = _repo(tmp_path, "x")
    _repo(tmp_path / "b", "x", with_wav=False)
    assert vtc.episodes_with_voice(root) == ["42"]


def test_real_scripts_parse():
    md = (vtc.ROOT / "episodes" / "ep09.md").read_text(encoding="utf-8")
    scripts = vtc.spoken_scripts(md)
    assert len(vtc.tokens(scripts["ar"], "ar")) > 40
    assert "balcony" in vtc.tokens(scripts["en"], "en")
