"""Engine v2 (EP06+) must never change EP01–EP05 (owner order, 1 Nov 2026)."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MC = ROOT / "master-claude"
spec = importlib.util.spec_from_file_location("frozen_check", ROOT / "tools" / "frozen_check.py")
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)


def ref():
    return json.loads(fc.REF.read_text())


def test_v1_engine_files_unchanged():
    assert fc.static_problems(ref()) == []


def test_reference_covers_every_frozen_episode_both_languages():
    keys = ref()["pixels"].keys()
    for nn in fc.FROZEN_EPISODES:
        for lang in ("AR", "EN"):
            assert sum(k.startswith(f"EP{nn}-{lang}@") for k in keys) == len(fc.FRAMES)


def test_changed_engine_file_is_caught(tmp_path, monkeypatch):
    r = ref()
    r["files"]["src/engine/types.ts"] = "0" * 64
    assert any("types.ts: changed" in p for p in fc.static_problems(r))


def test_old_episode_opting_into_v2_is_caught(tmp_path, monkeypatch):
    fake = tmp_path / "master-claude"
    (fake / "src" / "episodes").mkdir(parents=True)
    (fake / "src" / "episodes" / "ep03.ts").write_text("export const X = {engine: 2};")
    monkeypatch.setattr(fc, "MC", fake)
    probs = fc.static_problems({"files": {}})
    assert probs == ["ep03.ts opts into engine v2 — EP01–05 must stay on v1"]


def _ts_obj(src: str, name: str) -> dict:
    m = re.search(name + r": \{(.*?)\}", src, re.S)
    return dict(re.findall(r"(\w+): '(#[0-9A-Fa-f]{6})'", m.group(1)))


def test_ember_theme_is_exactly_the_v1_palette():
    types = (MC / "src/engine/types.ts").read_text()
    v1 = dict(re.findall(r"(\w+): '(#[0-9A-Fa-f]{6})'", types))
    theme = (MC / "src/engine2/theme.ts").read_text()
    assert "ember: {...V1," in theme  # ember spreads the v1 palette unchanged
    for k in v1:
        # no other theme may be missing a v1 role
        for name in ("electric", "gold", "mint"):
            assert k in _ts_obj(theme, name), (name, k)


def test_every_theme_defines_every_palette_key():
    theme = (MC / "src/engine2/theme.ts").read_text()
    keys = re.findall(r"^  (\w+): string;", theme.split("export type Palette")[1].split("};")[0], re.M)
    ember_extra = re.search(r"ember: \{\.\.\.V1, (.*?)\}", theme).group(1)
    for k in keys:
        if k in ("bg", "bg2", "orange", "blue", "green", "purple", "red", "white", "muted"):
            continue
        assert f"{k}:" in ember_extra, ("ember", k)
        for name in ("electric", "gold", "mint"):
            assert f"{k}:" in re.search(name + r": \{(.*?)\},\n", theme, re.S).group(1), (name, k)


def test_style_demos_are_not_episodes():
    idx = (MC / "src/episodes/index.ts").read_text()
    assert "DEMO" not in idx and "style-demos" not in idx
