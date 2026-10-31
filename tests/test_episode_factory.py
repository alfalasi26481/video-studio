import json
import shutil
import subprocess
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import episode_factory as ef  # noqa: E402

REAL = ef.ROOT

MD = """# EP09
## السكربت — عربي (نص النطق)

```
نص
```

## تعليق النشر

```
سطر أول عن Claude ✨
سطر ثانٍ 👇
#Claude #ذكاء_اصطناعي #برومبت #نصائح_تقنية #تعلم #إضافي
```

```
First line about Claude ✨
Second line 👇
#Claude #AI #AITips #AI
```
"""

TS = """export const EP09_AR: EpisodeData = {
  voice: 'vo/ep09_ar.wav',
  voiceDur: 20.5,
  clips: {hook: 'clips/ep09_hook.mp4', glitch: 'clips/ep01_glitch.mp4'},
  music: 'music/ep09_ar.wav',
};
export const EP09_EN: EpisodeData = {
  voice: 'vo/ep09_en.wav',
  voiceDur: 18.25,
  music: 'music/ep09_en.wav',
};
"""


@pytest.fixture
def root(tmp_path):
    (tmp_path / "episodes").mkdir()
    (tmp_path / "src/episodes").mkdir(parents=True)
    (tmp_path / "episodes/ep09.md").write_text(MD, encoding="utf-8")
    (tmp_path / "src/episodes/ep09.ts").write_text(TS, encoding="utf-8")
    (tmp_path / "src/episodes/index.ts").write_text("'EP09-AR': EP09_AR,\n'EP09-EN': EP09_EN,\n")
    words = [{"start": 0, "end": 1.5, "words": [[0, "توقف!"], [0.5, "Claude"]]},
             {"start": 1.5, "end": 62.25, "words": [[1.5, "تابعنا"]]}]
    for lang in ("ar", "en"):
        (tmp_path / f"src/episodes/ep09_words_{lang}.json").write_text(json.dumps(words), encoding="utf-8")
    for rel in ("vo/ep09_ar.wav", "vo/ep09_en.wav", "clips/ep09_hook.mp4", "clips/ep01_glitch.mp4",
                "music/ep09_ar.wav", "music/ep09_en.wav"):
        p = tmp_path / "public" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x")
    return tmp_path


# ---- preflight
def test_preflight_ready(root):
    assert ef.preflight("09", root) == []


def test_preflight_missing_assets_map_to_engine_steps(root):
    (root / "public/clips/ep09_hook.mp4").unlink()
    (root / "public/music/ep09_en.wav").unlink()
    (root / "src/episodes/ep09_words_en.json").unlink()
    (root / "src/episodes/index.ts").write_text("'EP09-AR': EP09_AR,\n")
    got = {(m.kind, m.step, m.path) for m in ef.preflight("09", root)}
    assert got == {("clips", 6, "public/clips/ep09_hook.mp4"), ("music", 7, "public/music/ep09_en.wav"),
                   ("words", 5, "src/episodes/ep09_words_en.json"),
                   ("registry", 4, "src/episodes/index.ts: EP09-EN")}


def test_preflight_new_episode(root):
    kinds = sorted(m.kind for m in ef.preflight("11", root))
    assert kinds == ["episode", "registry", "registry", "script", "words", "words"]


def test_preflight_real_engine_episodes_ready():
    for nn in ("01", "02"):
        assert ef.preflight(nn) == [], nn


# ---- captions / platforms
def test_post_captions_split_by_language():
    caps = ef.post_captions(MD)
    assert caps["ar"].startswith("سطر أول") and caps["en"].startswith("First line")


def test_post_captions_real_episodes():
    for nn in ("01", "02"):
        caps = ef.post_captions((REAL / f"episodes/ep{nn}.md").read_text(encoding="utf-8"))
        assert set(caps) == {"ar", "en"} and "#Claude" in caps["ar"] and "#Claude" in caps["en"]


def test_hashtags_deduplicated_and_capped():
    body, tags = ef.split_caption(ef.post_captions(MD)["en"])
    assert tags == ["#Claude", "#AI", "#AITips"] and body == ["First line about Claude ✨", "Second line 👇"]
    post = ef.platform_post(ef.post_captions(MD)["ar"], "instagram")
    assert len(ef._HASHTAG.findall(post)) == 5


def test_snapchat_short_first_line_only():
    post = ef.platform_post(ef.post_captions(MD)["ar"], "snapchat")
    assert "سطر ثانٍ" not in post and len(post) <= 160
    assert len(ef._HASHTAG.findall(post)) <= 3


def test_over_limit_drops_hashtags_then_refuses():
    long_line = "كلمة " * 30  # 150 chars
    post = ef.platform_post(long_line + "\n#Claude #ذكاء_اصطناعي #برومبت", "snapchat")
    assert len(post) <= 160 and post.startswith("كلمة")
    with pytest.raises(ValueError):
        ef.platform_post("كلمة " * 40, "snapchat")


# ---- srt
def test_srt_format_and_rtl_marks():
    srt = ef.to_srt([{"start": 0, "end": 1.5, "words": [[0, "توقف!"], [0.5, "Claude"]]},
                     {"start": 61.5, "end": 3725.042, "words": [[61.5, "تابعنا"]]}], rtl=True)
    assert "1\n00:00:00,000 --> 00:00:01,500\n‫توقف! Claude‬" in srt
    assert "2\n00:01:01,500 --> 01:02:05,042\n" in srt
    assert "‫" not in ef.to_srt([{"start": 0, "end": 1, "words": [[0, "Hi"]]}], rtl=False)


# ---- QA
EBUR = """[Parsed_ebur128_0 @ 0x1] t: 1.0 M: -20.0
[Parsed_ebur128_0 @ 0x1] Summary:

  Integrated loudness:
    I:         -14.1 LUFS
    Threshold: -24.1 LUFS

  True peak:
    Peak:       -1.6 dBFS
"""


def test_parse_ebur128():
    assert ef.parse_ebur128(EBUR) == (-14.1, -1.6)
    assert ef.parse_ebur128("Summary:\n I: -inf LUFS\n Peak: -inf dBFS") == (None, None)


def good(**kw):
    q = ef.QA("EP09-AR", 1080, 1920, 30.0, 21.0, True, -14.0, -1.5)
    for k, v in kw.items():
        setattr(q, k, v)
    return q


def test_judge_pass():
    assert ef.judge(good(), voice_dur=20.5).problems == []


@pytest.mark.parametrize("kw,needle", [
    ({"width": 1920, "height": 1080}, "size"), ({"fps": 25.0}, "fps"), ({"lufs": -16.0}, "loudness"),
    ({"peak": -0.5}, "true peak"), ({"has_audio": False}, "no audio"), ({"duration": 19.0}, "shorter"),
])
def test_judge_fail(kw, needle):
    probs = ef.judge(good(**kw), voice_dur=20.5).problems
    assert any(needle in p for p in probs), probs


def test_voice_dur_per_language(root):
    assert ef.voice_dur("09", "AR", root) == 20.5
    assert ef.voice_dur("09", "EN", root) == 18.25
    assert ef.voice_dur("02", "EN") == 25.73


def test_run_qa_missing_render(root):
    res = ef.run_qa("09", ("AR",), root)
    assert "render first" in res[0].problems[0]


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
def test_probe_real_file_flags_wrong_size_and_loudness(tmp_path):
    f = tmp_path / "x.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=540x960:r=25:d=1",
                    "-f", "lavfi", "-i", "sine=f=440:d=1", "-af", "volume=-30dB", "-shortest",
                    "-c:v", "libx264", "-c:a", "aac", str(f)], check=True)
    q = ef.judge(ef.probe(f, "X"))
    joined = " ".join(q.problems)
    assert q.has_audio and "size 540x960" in joined and "fps 25" in joined and "loudness" in joined


# ---- kit
def test_build_kit_writes_srt_and_posts(root):
    kit = ef.build_kit("09", root, qa=[good()])
    pub = (kit / "PUBLISH.md").read_text(encoding="utf-8")
    assert (kit / "EP09-AR.srt").exists() and (kit / "EP09-EN.srt").exists()
    for name in ("TikTok", "Instagram Reels", "Snapchat Spotlight"):
        assert pub.count(f"**{name}**") == 2
    assert "غير مؤكد" in pub and "EP09-AR: 1080x1920" in pub and "⚠️ فحص المحتوى" not in pub


def test_build_kit_runs_content_check(root):
    md = (root / "episodes/ep09.md").read_text(encoding="utf-8").replace("سطر ثانٍ", "أرسلها لمديرك في الدوام")
    (root / "episodes/ep09.md").write_text(md, encoding="utf-8")
    pub = (ef.build_kit("09", root) / "PUBLISH.md").read_text(encoding="utf-8")
    assert "⚠️ فحص المحتوى" in pub


def test_cli_preflight_exit_codes(root, capsys):
    assert ef.main(["preflight", "9", "--root", str(root)]) == 0
    assert ef.main(["preflight", "12", "--root", str(root)]) == 1
    assert "step  1" in capsys.readouterr().out
