import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import voice_level as vl  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
needs_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg missing")


def test_parse_ebur128_uses_summary():
    text = "t: 1 M: -30 I: -50.0 LUFS\nSummary:\n  Integrated loudness:\n    I:         -21.1 LUFS\n  True peak:\n    Peak:       -1.8 dBFS\n"
    assert vl.parse_ebur128(text) == (-21.1, -1.8)


def test_parse_ebur128_missing():
    with pytest.raises(ValueError):
        vl.parse_ebur128("nothing")


def test_verdict():
    assert vl.verdict(-19.6, -2.1) == []
    assert vl.verdict(-19.0, -2.0) == []
    assert any("loudness" in p for p in vl.verdict(-21.1, -2.5))
    assert any("peak" in p for p in vl.verdict(-19.6, -1.0))


@needs_ffmpeg
def test_fix_brings_quiet_peaky_voice_into_window(tmp_path):
    f = tmp_path / "v.wav"
    # quiet tone with a loud click: low integrated loudness, high peak (the EP04-AR shape)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "sine=f=220:d=6", "-f", "lavfi", "-i",
                    "sine=f=1000:d=0.05", "-filter_complex", "[0]volume=0.08[a];[1]volume=0.25,adelay=2000[b];[a][b]amix=2:normalize=0",
                    "-ar", "24000", "-ac", "1", str(f)], check=True)
    i0, _ = vl.measure(str(f))
    assert vl.verdict(i0, -9) != []
    assert vl.main([str(f)]) == 0  # report only, never a gate
    assert vl.main([str(f), "--fix"]) == 0
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=sample_rate,channels:format=duration",
                          "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout
    assert "24000,1" in out and "6.0" in out


@needs_ffmpeg
@pytest.mark.parametrize("ep", ["ep03_ar", "ep04_ar"])
def test_normalised_voices_at_reference(ep):
    p = ROOT / "master-claude/public/vo" / f"{ep}.wav"
    if not p.exists():
        pytest.skip("no file")
    assert vl.verdict(*vl.measure(str(p))) == []
