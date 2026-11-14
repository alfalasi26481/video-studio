import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import episode_factory as ef  # noqa: E402
import remaster as rm  # noqa: E402

M = {"input_i": "-18.6", "input_tp": "-3.5", "input_lra": "6.1", "input_thresh": "-28.9", "target_offset": "0.2"}


def test_parse_loudnorm_json_takes_last_block():
    err = "noise {not json}\n[Parsed_loudnorm_0]\n{\n\t\"input_i\" : \"-18.6\",\n\t\"input_tp\" : \"-3.5\"\n}\n"
    assert rm.parse_loudnorm_json(err)["input_i"] == "-18.6"


def test_parse_loudnorm_json_missing():
    with pytest.raises(ValueError):
        rm.parse_loudnorm_json("nothing here")


def test_second_pass_filter_is_linear_and_uses_measurement():
    f = rm.second_pass_filter(M)
    assert f.startswith("loudnorm=I=-14.0:TP=-3.0:LRA=9:linear=true")
    assert "measured_I=-18.6" in f and "measured_TP=-3.5" in f and "offset=0.2" in f


def test_audio_only_failure():
    ok = ef.QA("EP11-EN")
    peak = ef.QA("EP11-EN", problems=["true peak -0.6 dBTP (need < -1.0)"])
    both = ef.QA("EP11-EN", problems=["loudness -13.6 LUFS (need -14.0±0.3)", "true peak -0.6 dBTP (need < -1.0)"])
    size = ef.QA("EP11-EN", problems=["true peak -0.6 dBTP (need < -1.0)", "size 540x960 (need 1080x1920)"])
    assert not ef.audio_only_failure(ok)
    assert ef.audio_only_failure(peak) and ef.audio_only_failure(both)
    assert not ef.audio_only_failure(size)


def test_voice_dur_reads_engine_v2_episodes():
    # EpisodeDataV2 used to be skipped silently, so the duration-vs-voice check never ran from EP06 on.
    assert ef.voice_dur("11", "AR") == pytest.approx(30.05)
    assert ef.voice_dur("11", "EN") == pytest.approx(28.61)


def test_missing_raw(tmp_path):
    with pytest.raises(FileNotFoundError):
        rm.remaster_episode("11", "EN", tmp_path)


def test_trim_gain_corrects_dynamic_fallback_miss():
    # seed 24 (4 Nov 2026): loudnorm fell back to dynamic mode and landed -14.4 LUFS / -2.8 dBTP.
    assert rm.trim_gain(-14.4, -2.8) == pytest.approx(0.4)
    assert rm.trim_gain(-14.1, -2.4) == 0.0          # inside +-0.15: leave it
    assert rm.trim_gain(-13.6, -2.0) == pytest.approx(-0.4)


def test_trim_gain_never_pushes_peak_over_limit():
    # +0.9 dB would put the peak at -0.9 dBTP; cap the gain so the peak stays at -1.5.
    assert rm.trim_gain(-14.9, -1.8) == pytest.approx(0.3)


def _hot_raw(raw: Path, seed: int) -> None:
    # 6 s of loud, spiky audio: a hot master like the one that failed EP11-EN.
    # Fixed noise seed: the old random seed made this test pass ~19 runs in 20 (seed 24 fails).
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=30:d=6",
                    "-f", "lavfi", "-i", f"anoisesrc=d=6:c=pink:a=0.9:seed={seed}", "-f", "lavfi", "-i", "sine=f=220:d=6",
                    "-filter_complex", "[1:a][2:a]amix=inputs=2:normalize=0,volume=2[a]", "-map", "0:v", "-map", "[a]",
                    "-shortest", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", str(raw)], check=True)


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
@pytest.mark.parametrize("seed", [1, 3, 24])
def test_remaster_fixes_hot_peak_and_keeps_picture(tmp_path, seed):
    raw_dir = tmp_path / "out" / "raw"
    raw_dir.mkdir(parents=True)
    _hot_raw(raw_dir / "EP99-EN.mp4", seed)
    out = rm.remaster_episode("99", "EN", tmp_path)
    q = ef.judge(ef.probe(out, "EP99-EN"))
    assert (q.width, q.height, round(q.fps)) == (1080, 1920, 30)
    assert q.peak < -1.0 and abs(q.lufs + 14.0) <= 0.3, q
