import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import engine_content_check as ecc  # noqa: E402

MD = '''# الحلقة 9

## السكربت — عربي (نص النطق)

```
توقف! هذا نص الحلقة.
```

## سطور الترجمة

```json
[[0,"توقف! سطر أول"],[2.5,"سطر ثانٍ"]]
```

| `ep09_hook.mp4` | Glowing city skyline of a big company, cinematic, no text, no people |

## الموسيقى

```
python3 scripts/music.py public/music/ep09_ar.wav 7 20 24 30
```
'''

TS = '''import {COLORS} from '../engine/types';
import wAr from './ep09_words_ar.json';
// تعليق: وزارة (لا يظهر على الشاشة)
const clips = {hook: 'clips/ep09_hook.mp4'};
export const EP09_AR = {
  lang: 'ar',
  dir: 'rtl',
  text: {stop: 'توقف!', hookSub: "You're doing it wrong", emailSubject: 'رسالة إلى مديرك'},
  steps: [{label: 'الدور', icon: 'role', color: COLORS.orange}],
};
'''


def test_md_texts_reads_script_and_caption_lines_only():
    texts = ecc.md_texts(MD)
    assert "توقف! هذا نص الحلقة." in texts
    assert "توقف! سطر أول" in texts and "سطر ثانٍ" in texts
    assert not any("python3" in t for t in texts)
    assert not any("company" in t for t in texts)  # clip prompts are never shown


def test_ts_texts_skips_paths_enums_and_comments():
    texts = ecc.ts_texts(TS)
    assert "توقف!" in texts and "You're doing it wrong" in texts and "الدور" in texts
    for skipped in ("ar", "rtl", "role", "clips/ep09_hook.mp4", "../engine/types"):
        assert skipped not in texts
    assert not any("وزارة" in t for t in texts)


def _episode(tmp_path, md, ts, nn="09"):
    (tmp_path / "episodes").mkdir()
    (tmp_path / "src" / "episodes").mkdir(parents=True)
    (tmp_path / "episodes" / f"ep{nn}.md").write_text(md, encoding="utf-8")
    (tmp_path / "src" / "episodes" / f"ep{nn}.ts").write_text(ts, encoding="utf-8")
    return tmp_path


def test_flags_work_topic_in_on_screen_text(tmp_path):
    root = _episode(tmp_path, MD, TS)
    flags = ecc.check_episode("09", root)
    assert [f.code for f in flags] == ["WORK"]
    assert flags[0].source == "ep09.ts"


def test_flags_dialect_and_org_in_script(tmp_path):
    md = MD.replace("هذا نص الحلقة.", "شلون تكتب لبنك؟")
    root = _episode(tmp_path, md, "export const X = {stop: 'توقف!'};\n")
    codes = sorted(f.code for f in ecc.check_episode("09", root))
    assert codes == ["DIALECT", "ORG"]


def test_all_episode_ids(tmp_path):
    root = _episode(tmp_path, MD, TS)
    (root / "src" / "episodes" / "ep09_words_ar.ts").write_text("", encoding="utf-8")
    assert ecc.all_episode_ids(root) == ["09"]


def test_approved_engine_episodes_are_listed():
    ids = ecc.all_episode_ids()
    assert "01" in ids and "02" in ids
