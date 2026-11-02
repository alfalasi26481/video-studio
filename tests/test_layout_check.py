"""Rules of tools/layout_check.py on synthetic measurements (no browser needed)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import layout_check as lc  # noqa: E402


def T(t="كلمة", x0=300, y0=600, x1=500, y1=660, box=None):
    return {"t": t, "x0": x0, "y0": y0, "x1": x1, "y1": y1, "opacity": 1, "box": box}


def M(*frames, step=6):
    return {"id": "EP99-AR", "fps": 30, "step": step,
            "frames": [{"f": i * step, "texts": list(ts)} for i, ts in enumerate(frames)]}


def rules(m):
    return [(f.rule, f.severity, f.text) for f in lc.evaluate(m)]


def test_safe_text_has_no_findings():
    assert rules(M([T()], [T()], [T()])) == []


def test_bottom_zone_is_error():
    t = T(y0=1500, y1=1560)
    assert rules(M([t], [t])) == [("bottom", "error", "كلمة")]


def test_text_ending_exactly_at_80_percent_is_fine():
    t = T(y0=1480, y1=1536)
    assert rules(M([t], [t])) == []


def test_right_rail_is_warning_only_inside_its_band():
    rail = T(x0=800, x1=1000, y0=1000, y1=1060)
    high = T(t="عنوان", x0=800, x1=1000, y0=300, y1=360)   # right edge but above 40%
    assert rules(M([rail, high], [rail, high])) == [("right-rail", "warning", "كلمة")]


def test_top_band_is_warning():
    t = T(y0=60, y1=120)
    assert rules(M([t], [t])) == [("top", "warning", "كلمة")]


def test_off_canvas_word():
    t = T(t="cut", x0=1000, x1=1120, y0=300, y1=360)
    assert ("off-canvas", "error", "cut") in rules(M([t], [t]))


def test_spill_out_of_card():
    t = T(t="long", x0=100, x1=640, box=[120, 580, 620, 700])
    f = lc.evaluate(M([t], [t]))
    assert [(x.rule, x.text) for x in f] == [("spill", "long")]
    assert f[0].depth == 20


def test_small_overhang_within_tolerance_is_ignored():
    t = T(x0=100, x1=624, box=[100, 580, 620, 700])  # 4 px
    assert rules(M([t], [t])) == []


def test_single_frame_glitch_from_camera_shake_is_ignored():
    bad = T(y0=1500, y1=1600)
    assert rules(M([T()], [bad], [T()])) == []


def test_run_must_be_consecutive():
    bad = T(y0=1500, y1=1600)
    assert rules(M([bad], [T()], [bad], [T()])) == []
    f = lc.evaluate(M([T()], [bad], [bad], [bad]))
    assert len(f) == 1 and (f[0].first_frame, f[0].last_frame) == (6, 18)


def test_depth_is_median_so_a_whip_frame_does_not_dominate():
    a = T(y0=1500, y1=1546)          # 10 px in
    whip = T(y0=1500, y1=1900)       # transition frame
    f = lc.evaluate(M([a], [a], [whip]))
    assert f[0].depth == 10


def test_errors_sort_before_warnings_and_exit_codes(tmp_path, capsys):
    import json
    warn = T(t="w", x0=800, x1=1000, y0=1000, y1=1060)
    err = T(t="e", y0=1500, y1=1600)
    m = M([warn, err], [warn, err])
    assert [f.severity for f in lc.evaluate(m)] == ["error", "warning"]
    p = tmp_path / "m.json"
    p.write_text(json.dumps(m))
    assert lc.main(["--json", str(p)]) == 1
    p.write_text(json.dumps(M([warn], [warn])))
    assert lc.main(["--json", str(p)]) == 0


def test_page_errors_fail_but_media_errors_are_noise(tmp_path):
    import json
    m = M([T()], [T()])
    m["errors"] = ["MediaPlaybackError: clip not served"]
    p = tmp_path / "m.json"
    p.write_text(json.dumps(m))
    assert lc.main(["--json", str(p)]) == 0
    m["errors"].append("TypeError: x is undefined")
    p.write_text(json.dumps(m))
    assert lc.main(["--json", str(p)]) == 1


def test_all_compositions_read_from_registry():
    ids = lc.all_compositions()
    assert {"EP01-AR", "EP01-EN", "EP02-AR", "EP02-EN"} <= set(ids)


def test_text_touching_the_side_edge_is_error():
    # EP07-EN «LIKE THIS?» measured at x0≈-1 (inside the 1 px tolerance) and came out cut in the render
    t = T(t="LIKE THIS?", x0=-1, x1=522, y0=400, y1=620)
    assert rules(M([t], [t])) == [("edge", "error", "LIKE THIS?")]
    r = T(t="right", x0=600, x1=1075, y0=300, y1=360)
    assert rules(M([r], [r])) == [("edge", "error", "right")]


def test_text_with_edge_margin_is_fine_and_off_canvas_is_not_double_counted():
    ok = T(x0=12, x1=1068, y0=300, y1=360)
    assert rules(M([ok], [ok])) == []
    cut = T(t="cut", x0=-40, x1=400, y0=300, y1=360)
    assert rules(M([cut], [cut])) == [("off-canvas", "error", "cut")]


# --- ids: the episode number is accepted, not only the full composition id (cycle 22) ---
AVAILABLE = ["EP08-AR", "EP08-EN", "EP09-AR", "EP09-EN"]


def test_episode_number_expands_to_both_languages():
    assert lc.resolve_ids(["09"], AVAILABLE) == ["EP09-AR", "EP09-EN"]
    assert lc.resolve_ids(["9"], AVAILABLE) == ["EP09-AR", "EP09-EN"]
    assert lc.resolve_ids(["ep09"], AVAILABLE) == ["EP09-AR", "EP09-EN"]


def test_full_composition_id_is_kept_and_normalised():
    assert lc.resolve_ids(["EP09-AR"], AVAILABLE) == ["EP09-AR"]
    assert lc.resolve_ids(["ep08-en"], AVAILABLE) == ["EP08-EN"]


def test_no_ids_means_all_and_duplicates_are_dropped():
    assert lc.resolve_ids([], AVAILABLE) == AVAILABLE
    assert lc.resolve_ids(["09", "EP09-AR"], AVAILABLE) == ["EP09-AR", "EP09-EN"]


def test_unknown_episode_is_a_clear_error():
    import pytest
    with pytest.raises(ValueError, match="EP10"):
        lc.resolve_ids(["10"], AVAILABLE)
