import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import clip_status as cs  # noqa: E402

OWN = ("const clips = {hook: 'clips/ep07_hook.mp4', glitch: 'clips/ep01_glitch.mp4', "
       "mid: 'clips/ep07_mid.mp4', burst: 'clips/ep07_burst.mp4', outro: 'clips/ep01_outro.mp4'};")
PLACEHOLDER = ("const clips = {hook: 'clips/ep01_hook.mp4', glitch: 'clips/ep01_glitch.mp4', "
               "mid: 'clips/ep01_beams.mp4', burst: 'clips/ep01_burst.mp4', outro: 'clips/ep01_outro.mp4'};")


def _public(tmp_path, names):
    d = tmp_path / "public" / "clips"
    d.mkdir(parents=True)
    for n in names:
        (d / n).write_bytes(b"x")
    return tmp_path / "public"


ALL = ["ep01_hook.mp4", "ep01_glitch.mp4", "ep01_beams.mp4", "ep01_burst.mp4", "ep01_outro.mp4",
       "ep07_hook.mp4", "ep07_mid.mp4", "ep07_burst.mp4"]


def test_clips_parsed_from_ts():
    assert cs.clips_from_ts(OWN)["mid"] == "clips/ep07_mid.mp4"
    assert cs.clips_from_ts("const x = 1;") == {}


def test_own_clips_with_shared_glitch_and_outro_are_own(tmp_path):
    s = cs.status_of(7, OWN, _public(tmp_path, ALL))
    assert s.own and s.missing == []


def test_ep01_shots_on_a_later_episode_are_placeholder(tmp_path):
    s = cs.status_of(7, PLACEHOLDER, _public(tmp_path, ALL))
    assert s.borrowed == ["hook", "mid", "burst"]


def test_missing_clip_file_is_error(tmp_path):
    s = cs.status_of(7, OWN, _public(tmp_path, ALL[:-1]))
    assert s.missing == ["clips/ep07_burst.mp4"]
    _, errors, _, _ = cs.report([s], lambda n: True)
    assert errors == 1


def test_credits_only_for_approved_placeholders(tmp_path):
    pub = _public(tmp_path, ALL)
    a, b = cs.status_of(7, PLACEHOLDER, pub), cs.status_of(9, PLACEHOLDER.replace("ep07", "ep09"), pub)
    lines, errors, warnings, credits = cs.report([a, b], lambda n: n == 7)
    assert (errors, warnings, credits) == (0, 1, 48.75)
    assert any("[info] EP09" in ln for ln in lines)


def test_real_repo_has_no_missing_clip_files():
    assert all(not s.missing for s in cs.collect())
