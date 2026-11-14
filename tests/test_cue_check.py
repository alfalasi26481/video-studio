import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import cue_check as cc  # noqa: E402

GOOD = {"problem": 2.0, "typeAt": 2.4, "badAt": 5.0, "formula": 7.0, "steps": [9.0, 13.0, 17.0], "diff": 21.0, "cta": 25.0}
LINES = [{"start": s, "end": s + 1, "words": [[s, "w"]]} for s in [0.0, 2.0, 5.0, 7.0, 9.0, 13.0, 17.0, 21.0, 25.0]]


def test_good_episode_passes():
    assert cc.check_episode(GOOD, 28.0, LINES) == ([], [])


def test_steps_out_of_order_is_error():
    errs, _ = cc.check_episode({**GOOD, "steps": [9.0, 17.0, 13.0]}, 28.0, LINES)
    assert any("steps[1]" in e for e in errs)


def test_cta_after_voice_is_error():
    errs, _ = cc.check_episode(GOOD, 24.0, LINES)
    assert any("voiceDur" in e for e in errs)


def test_caption_past_voice_is_error():
    errs, _ = cc.check_episode(GOOD, 25.5, LINES + [{"start": 26, "end": 27, "words": [[26.0, "x"]]}])
    assert any("last caption word" in e for e in errs)


def test_decreasing_caption_starts_is_error():
    bad = LINES[:3] + [{"start": 1.0, "end": 2, "words": [[1.0, "x"]]}] + LINES[3:]
    errs, _ = cc.check_episode(GOOD, 28.0, bad)
    assert any("not increasing" in e for e in errs)


def test_mid_sentence_cue_is_warning_only():
    errs, warns = cc.check_episode({**GOOD, "diff": 22.0}, 28.0, LINES)
    assert errs == [] and any("diff=22.0" in w for w in warns)


def test_typeat_is_not_aligned():
    assert cc.check_episode({**GOOD, "typeAt": 3.3}, 28.0, LINES) == ([], [])


def test_parse_ts_reads_real_episode():
    eps = cc.parse_ts((cc.EPS / "ep13.ts").read_text(encoding="utf-8"))
    assert [(n, l) for n, l, *_ in eps] == [("EP13_AR", "ar"), ("EP13_EN", "en")]
    _, _, vd, cues, wf = eps[0]
    assert vd == 31.05 and cues["steps"] == [10.62, 14.6, 19.1] and wf == "ep13_words_ar.json"


def test_repo_has_no_cue_errors():
    assert cc.main(["cue_check"]) == 0
