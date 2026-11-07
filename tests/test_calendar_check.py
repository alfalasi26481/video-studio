import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import calendar_check as cc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TODAY = dt.date(2026, 11, 4)


def pid(n: int) -> str:
    return f"cmw{n:022d}"


def run(md: str, today: dt.date = TODAY, episodes: Path = ROOT / "master-claude" / "episodes"):
    posts, problems = cc.parse(md)
    assert problems == []
    return [(lvl, rule) for lvl, rule, _ in cc.check(posts, today, episodes)]


def channel_table(title: str, rows: list[tuple[str, str, str]]) -> str:
    out = [f"### {title}", "| الموعد (UTC) | الحلقة | Postiz id |", "|---|---|---|"]
    out += [f"| {w} | {lbl} | {i} |" for w, lbl, i in rows]
    return "\n".join(out) + "\n"


def test_clean_schedule_passes():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP03 أربع عادات", pid(1))])
    md += channel_table("تيك توك الإنجليزي", [("2026-11-08 18:00", "EN EP03 Four habits", pid(2))])
    assert run(md) == []


def test_english_post_on_arabic_account_is_error():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "EN EP03 Four habits", pid(1))])
    assert ("error", "lang") in run(md)


def test_arabic_label_without_prefix_reads_as_arabic():
    md = channel_table("تيك توك الإنجليزي", [("2026-11-08 18:00", "تحقق قبل أن تثق", pid(1))])
    assert ("error", "lang") in run(md)


def test_same_episode_twice_on_one_channel():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP03 أ", pid(1)),
                                           ("2026-11-10 16:00", "AR EP03 ب", pid(2))])
    assert ("error", "dup-ep") in run(md)


def test_same_episode_on_two_channels_is_fine():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP03 أ", pid(1))])
    md += channel_table("تيك توك العربي", [("2026-11-08 16:00", "AR EP03 أ", pid(2))])
    assert run(md) == []


def test_two_posts_in_one_slot():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP03 أ", pid(1)),
                                           ("2026-11-08 16:00", "AR EP04 ب", pid(2))])
    assert ("error", "dup-slot") in run(md)


def test_deleted_id_column_removes_the_old_post():
    """The 4 Nov cycle re-created posts and recorded the old ids as deleted."""
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP03 أ", pid(1))])
    md += ("## دورة 4 نوفمبر 2026\n"
           "| الموعد (UTC) | الحلقة | القناة | id جديد | id محذوف |\n|---|---|---|---|---|\n"
           f"| 11-10 16:00 | AR EP03 أ | إنستغرام AR | {pid(2)} | {pid(1)} |\n")
    posts, _ = cc.parse(md)
    live = cc.current(posts)
    assert [p.post_id for p in live] == [pid(2)]
    assert live[0].when == dt.datetime(2026, 11, 10, 16, 0)  # year from the heading
    assert run(md) == []


def test_unknown_episode_number():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP99 لا توجد", pid(1))])
    assert ("error", "no-ep") in run(md)


def test_future_slot_and_weekday_warnings_only():
    md = channel_table("إنستغرام الإنجليزي", [("2026-11-09 16:00", "EN EP03 Four habits", pid(1))])
    found = run(md)
    assert ("warning", "time") in found and ("warning", "weekday") in found
    assert not any(lvl == "error" for lvl, _ in found)


def test_past_posts_are_not_held_to_the_new_slot():
    md = channel_table("إنستغرام الإنجليزي", [("2026-11-02 16:00", "EN EP03 Four habits", pid(1))])
    assert run(md) == []


def test_tables_without_a_schedule_are_ignored():
    md = ("| المنصة | العربي | الإنجليزي |\n|---|---|---|\n| تيك توك | @x | جديد |\n"
          "| ما الناقص | لماذا | ما يفعله |\n|---|---|---|\n| حساب | تحقق | ينشئه |\n")
    posts, problems = cc.parse(md)
    assert posts == [] and problems == []


def test_unknown_channel_language_is_reported():
    md = channel_table("حساب ما", [("2026-11-08 16:00", "AR EP03 أ", pid(1))])
    posts, problems = cc.parse(md)
    assert posts == [] and len(problems) == 1


def test_real_calendar_passes():
    assert cc.main(["--today", "2026-11-04"]) == 0


# --- runway (5 Nov 2026): how many days of scheduled posts are left per account

def runway(md: str, today: dt.date = TODAY, days: int = 7):
    posts, _ = cc.parse(md)
    return cc.runway(posts, today, days)


def test_runway_warns_when_account_schedule_ends_within_days():
    md = channel_table("تيك توك العربي", [("2026-11-08 16:00", "AR EP03 أربع عادات", pid(1))])
    out = runway(md)
    assert [(lvl, rule) for lvl, rule, _ in out] == [("warning", "runway")]
    assert "2026-11-08" in out[0][2] and "4 day" in out[0][2]


def test_runway_quiet_when_schedule_reaches_beyond_days():
    md = channel_table("تيك توك العربي", [("2026-11-20 16:00", "AR EP03 أربع عادات", pid(1))])
    assert runway(md) == []


def test_runway_is_per_account():
    md = channel_table("تيك توك العربي", [("2026-11-20 16:00", "AR EP03 أربع عادات", pid(1))])
    md += channel_table("إنستغرام الإنجليزي", [("2026-11-06 18:00", "EN EP03 Four habits", pid(2))])
    out = runway(md)
    assert len(out) == 1 and "instagram-en" in out[0][2]


def test_runway_flags_account_with_nothing_left():
    md = channel_table("إنستغرام العربي", [("2026-11-01 16:00", "AR EP01 المعادلة", pid(1))])
    out = runway(md)
    assert len(out) == 1 and "nothing scheduled" in out[0][2]


def test_runway_ignores_deleted_posts():
    md = ("### إنستغرام العربي\n| الموعد (UTC) | الحلقة | Postiz id | id محذوف |\n|---|---|---|---|\n"
          f"| 2026-11-20 16:00 | AR EP03 أربع عادات | {pid(1)} | |\n"
          f"| 2026-11-06 16:00 | AR EP04 المشاريع | {pid(2)} | {pid(1)} |\n")
    out = runway(md)
    assert len(out) == 1 and "2026-11-06" in out[0][2]


def test_main_prints_runway_and_stays_green(tmp_path, capsys):
    f = tmp_path / "CALENDAR.md"
    f.write_text(channel_table("تيك توك العربي", [("2026-11-08 16:00", "AR EP03 أربع عادات", pid(1))]),
                 encoding="utf-8")
    assert cc.main(["--file", str(f), "--today", "2026-11-04"]) == 0
    out = capsys.readouterr().out
    assert "[warning] runway" in out and "1 warning(s)" in out


# --- gap: an episode skipped inside an account's own run (5 Nov 2026: EP03-AR
#     on Instagram, missing between EP02 and EP04 on Arabic TikTok) ---

def gaps(md: str):
    posts, problems = cc.parse(md)
    assert problems == []
    return cc.gaps(posts)


def test_gap_flags_episode_skipped_between_neighbours():
    md = channel_table("تيك توك العربي", [("2026-11-03 16:00", "EP02 الجملة", pid(1)),
                                          ("2026-11-08 16:00", "AR EP04 المشاريع", pid(2))])
    out = gaps(md)
    assert [(lvl, rule) for lvl, rule, _ in out] == [("warning", "gap")]
    assert "EP03" in out[0][2] and "tiktok-ar" in out[0][2]


def test_gap_names_sibling_account_that_has_it():
    md = channel_table("إنستغرام العربي", [("2026-11-08 16:00", "AR EP03 أربع عادات", pid(1))])
    md += channel_table("تيك توك العربي", [("2026-11-03 16:00", "EP02 الجملة", pid(2)),
                                           ("2026-11-08 16:00", "AR EP04 المشاريع", pid(3))])
    out = gaps(md)
    assert len(out) == 1 and "instagram-ar" in out[0][2]


def test_gap_quiet_for_account_that_started_later():
    md = channel_table("يوتيوب العربي", [("2026-11-08 16:00", "AR EP04 المشاريع", pid(1)),
                                         ("2026-11-10 16:00", "AR EP05 Artifact", pid(2))])
    assert gaps(md) == []


def test_gap_ignores_deleted_posts():
    md = ("### تيك توك العربي\n| الموعد (UTC) | الحلقة | Postiz id | id محذوف |\n|---|---|---|---|\n"
          f"| 2026-11-03 16:00 | EP02 الجملة | {pid(1)} | |\n"
          f"| 2026-11-05 16:00 | AR EP03 عادات | {pid(2)} | |\n"
          f"| 2026-11-08 16:00 | AR EP04 المشاريع | {pid(3)} | {pid(2)} |\n")
    assert [r for _, r, _ in gaps(md)] == ["gap"]


def test_gap_is_a_warning_in_main(tmp_path, capsys):
    f = tmp_path / "CALENDAR.md"
    f.write_text(channel_table("تيك توك العربي", [("2026-11-20 16:00", "EP02 الجملة", pid(1)),
                                                 ("2026-11-22 16:00", "AR EP04 المشاريع", pid(2))]),
                 encoding="utf-8")
    assert cc.main(["--file", str(f), "--today", "2026-11-04"]) == 0
    assert "[warning] gap" in capsys.readouterr().out


# --- plan: next free cadence slots per account (5 Nov 2026, every feed ends 15 Nov) ---

def episodes_dir(statuses: dict[int, str], last: int = 15) -> Path:
    """A throwaway episodes folder: every epNN.md approved unless overridden."""
    import tempfile
    d = Path(tempfile.mkdtemp())
    for n in range(1, last + 1):
        word = statuses.get(n, "معتمدة من المالك")
        (d / f"ep{n:02d}.md").write_text(f"# الحلقة {n} — عنوان / Title\n\n- الحالة: **{word}** (تجربة)\n",
                                         encoding="utf-8")
    return d


ALL_APPROVED = episodes_dir({})


def plan(md: str, today: dt.date = TODAY, count: int = 3, last_ep: int = 15, episodes: Path = ALL_APPROVED):
    posts, problems = cc.parse(md)
    assert problems == []
    return [(c, f"{w:%Y-%m-%d %H:%M}", ep)
            for c, w, ep in cc.plan(posts, today, count=count, last_ep=last_ep, episodes=episodes)]


def test_plan_continues_after_last_post_on_cadence():
    md = channel_table("إنستغرام العربي", [("2026-11-12 16:00", "AR EP05", pid(1)),
                                            ("2026-11-15 16:00", "AR EP06", pid(2))])
    # 15 Nov is a Sunday -> Tue 17, Thu 19, Sun 22
    assert plan(md) == [("instagram-ar", "2026-11-17 16:00", 7),
                        ("instagram-ar", "2026-11-19 16:00", 8),
                        ("instagram-ar", "2026-11-22 16:00", 9)]


def test_plan_uses_english_slot_time():
    md = channel_table("تيك توك الإنجليزي", [("2026-11-15 18:00", "EN EP06 Upload", pid(1))])
    assert plan(md, count=1) == [("tiktok-en", "2026-11-17 18:00", 7)]


def test_plan_fills_a_gap_first():
    md = channel_table("تيك توك العربي", [("2026-11-10 16:00", "AR EP05", pid(1)),
                                           ("2026-11-12 16:00", "AR EP07", pid(2))])
    assert [ep for _, _, ep in plan(md)] == [6, 8, 9]


def test_plan_stops_at_last_episode_file():
    md = channel_table("إنستغرام العربي", [("2026-11-15 16:00", "AR EP14", pid(1))])
    assert [ep for _, _, ep in plan(md, count=5)] == [15]


def test_plan_starts_from_today_when_the_feed_is_dry():
    md = channel_table("إنستغرام العربي", [("2026-11-01 16:00", "AR EP06", pid(1))])
    # 4 Nov (Wed) is today; feed ended 1 Nov -> next cadence slot is Thu 5 Nov
    assert plan(md, count=1) == [("instagram-ar", "2026-11-05 16:00", 7)]


def test_plan_on_real_calendar_starts_after_15_nov():
    posts, _ = cc.parse(cc.CALENDAR.read_text(encoding="utf-8"))
    rows = cc.plan(posts, dt.date(2026, 11, 5), count=1)
    assert rows, "every account should get a proposal"
    for channel, when, ep in rows:
        assert when.date() > dt.date(2026, 11, 15)
        assert when.weekday() in cc.CADENCE
        assert (when.hour, when.minute) == cc.SLOT[channel.rsplit("-", 1)[-1]]
        assert ep >= 7


def test_plan_cli_prints_pasteable_rows(capsys):
    assert cc.main(["--plan", "1", "--today", "2026-11-05"]) == 0
    out = capsys.readouterr().out
    assert "| الموعد (UTC) | الحلقة | القناة | id جديد | id محذوف |" in out
    assert "EP07" in out


# --- approval gate (5 Nov 2026: --plan proposed EP08 «مسودة v2» and EP09 for 19/22 Nov) ---

def test_status_reads_bold_word():
    d = episodes_dir({8: "مسودة v2"}, last=9)
    assert cc.status(8, d) == "مسودة v2"
    assert cc.approved(7, d) and not cc.approved(8, d)
    assert cc.status(20, d) == "" and not cc.approved(20, d)


def test_plan_skips_unapproved_episodes():
    d = episodes_dir({8: "مسودة v2", 9: "معاينة مرندرة"})
    md = channel_table("إنستغرام العربي", [("2026-11-15 16:00", "AR EP06", pid(1))])
    assert [ep for _, _, ep in plan(md, episodes=d)] == [7, 10, 11]


def test_plan_does_not_fill_a_gap_with_a_draft():
    d = episodes_dir({6: "مسودة"})
    md = channel_table("تيك توك العربي", [("2026-11-10 16:00", "AR EP05", pid(1)),
                                           ("2026-11-12 16:00", "AR EP07", pid(2))])
    assert [ep for _, _, ep in plan(md, episodes=d)] == [8, 9, 10]


def test_held_lists_unscheduled_drafts_only():
    d = episodes_dir({4: "مسودة", 8: "مسودة v2"}, last=9)
    posts, _ = cc.parse(channel_table("إنستغرام العربي", [("2026-11-01 16:00", "AR EP04", pid(1)),
                                                          ("2026-11-03 16:00", "AR EP06", pid(2))]))
    assert cc.held(posts, episodes=d) == [8]


def test_future_post_of_unapproved_episode_is_error():
    d = episodes_dir({8: "مسودة v2"}, last=9)
    md = channel_table("إنستغرام العربي", [("2026-11-19 16:00", "AR EP08", pid(1))])
    assert ("error", "unapproved") in run(md, episodes=d)


def test_past_post_is_not_rechecked_for_approval():
    d = episodes_dir({8: "مسودة v2"}, last=9)
    md = channel_table("إنستغرام العربي", [("2026-11-01 16:00", "AR EP08", pid(1))])
    assert ("error", "unapproved") not in run(md, episodes=d)


def test_real_episodes_approval_matches_status_lines():
    real = ROOT / "master-claude" / "episodes"
    assert cc.approved(7, real) and cc.approved(15, real)
    # EP08–EP10 approved 6 Nov 2026 after the critic passes (status «معتمدة 6 نوفمبر 2026»)
    assert all(cc.approved(n, real) for n in (8, 9, 10))


def test_plan_cli_lists_held_episodes(capsys, monkeypatch):
    d = episodes_dir({8: "مسودة v2"}, last=15)
    monkeypatch.setattr(cc, "EPISODES", d)
    monkeypatch.setattr(cc.status, "__defaults__", (d,))
    monkeypatch.setattr(cc.approved, "__defaults__", (d,))
    monkeypatch.setattr(cc.held, "__defaults__", (None, d))
    monkeypatch.setattr(cc.plan, "__defaults__", (3, None, d))
    monkeypatch.setattr(cc.last_episode, "__defaults__", (d,))
    monkeypatch.setattr(cc.episode_title, "__defaults__", (d,))
    assert cc.main(["--plan", "3", "--today", "2026-11-05"]) == 0
    out = capsys.readouterr().out
    assert "held (not approved, never proposed): EP08" in out
    rows = [l for l in out.splitlines() if l.startswith("| 11-")]
    assert rows and not any("EP08" in l for l in rows)


def _when(s):
    return dt.datetime.fromisoformat(s)


def test_decide_by_uses_first_slot_per_episode():
    rows = [("instagram-en", _when("2026-11-17 18:00"), 7),
            ("tiktok-ar", _when("2026-11-17 16:00"), 7),
            ("tiktok-ar", _when("2026-11-19 16:00"), 11)]
    assert cc.decide_by(rows) == [(7, dt.date(2026, 11, 15), _when("2026-11-17 16:00")),
                                  (11, dt.date(2026, 11, 17), _when("2026-11-19 16:00"))]


def test_decide_by_lead_days_and_empty():
    rows = [("tiktok-ar", _when("2026-11-17 16:00"), 7)]
    assert cc.decide_by(rows, 5)[0][1] == dt.date(2026, 11, 12)
    assert cc.decide_by([]) == []


def test_plan_cli_prints_decide_by_and_flags_past(capsys):
    rc = cc.main(["--plan", "1", "--today", "2026-11-16"])
    out = capsys.readouterr().out
    assert rc == 0
    line = [l for l in out.splitlines() if l.startswith("decide by")]
    assert line and "EP07" in line[0] and "PAST" in line[0]


def status_table(title: str, rows: list[tuple[str, str, str, str]]) -> str:
    out = [f"## {title}", "| الموعد (UTC) | الحلقة | Postiz id | الحالة |", "|---|---|---|---|"]
    out += [f"| {w} | {lbl} | {i} | {s} |" for w, lbl, i, s in rows]
    return "\n".join(out) + "\n"


def unconfirmed(md: str, today: dt.date = TODAY):
    posts, _ = cc.parse(md)
    return cc.unconfirmed(posts, today)


def test_past_post_marked_published_is_confirmed():
    md = status_table("إنستغرام العربي", [("2026-10-31 16:00", "التعريف", pid(1), "منشور")])
    assert unconfirmed(md) == []


def test_past_post_still_scheduled_is_unconfirmed():
    md = status_table("إنستغرام العربي", [("2026-11-01 16:00", "EP01 المعادلة", pid(1), "مجدول (من جلسة سابقة)"),
                                          ("2026-11-03 16:00", "EP02 الجملة", pid(2), "مجدول")])
    out = unconfirmed(md)
    assert [(lvl, rule) for lvl, rule, _ in out] == [("warning", "unconfirmed")]
    assert "2 past post(s)" in out[0][2] and "11-01 EP01" in out[0][2] and "11-03 EP02" in out[0][2]


def test_table_without_status_column_counts_as_unconfirmed():
    md = channel_table("تيك توك العربي", [("2026-11-03 16:00", "EP02 الجملة السحرية", pid(1))])
    assert len(unconfirmed(md)) == 1


def test_future_and_today_posts_are_not_asked_for():
    md = status_table("إنستغرام العربي", [("2026-11-04 16:00", "AR EP03 أ", pid(1), "مجدول"),
                                          ("2026-11-08 16:00", "AR EP04 ب", pid(2), "مجدول")])
    assert unconfirmed(md) == []


def test_deleted_post_is_not_asked_for():
    md = channel_table("تيك توك العربي", [("2026-11-03 16:00", "EP02 أ", pid(1))])
    md += "\n| الموعد (UTC) | الحلقة | القناة | id جديد | id محذوف |\n|---|---|---|---|---|\n"
    md += f"| 11-10 16:00 | AR EP02 أ | تيك توك AR | {pid(2)} | {pid(1)} |\n"
    assert unconfirmed(md) == []


def test_unconfirmed_is_one_warning_per_account_in_main(capsys, tmp_path):
    f = tmp_path / "c.md"
    f.write_text(channel_table("إنستغرام العربي", [("2026-11-01 16:00", "EP01 أ", pid(1))])
                 + channel_table("تيك توك العربي", [("2026-11-01 16:00", "EP01 أ", pid(2))]), encoding="utf-8")
    assert cc.main(["--file", str(f), "--today", "2026-11-04", "--runway-days", "0"]) == 0
    assert capsys.readouterr().out.count("unconfirmed:") == 2


# --- source-age: the official page re-opened close to the post date (7 Nov 2026) ---

def _ep(tmp: Path, n: int, reviewed: str, state: str = "معتمدة 1 نوفمبر") -> None:
    (tmp / f"ep{n:02d}.md").write_text(
        f"# الحلقة {n} — عنوان / Title\n\n- الحالة: **{state}**\n"
        f"- المصدر الرسمي (رُوجع {reviewed}): https://support.claude.com/en/articles/1\n",
        encoding="utf-8")


def test_source_reviewed_long_before_post_warns_once_per_episode(tmp_path):
    _ep(tmp_path, 7, "2026-11-01")
    md = channel_table("إنستغرام العربي", [("2026-11-26 16:00", "AR EP07 بحث", pid(1))])
    md += channel_table("تيك توك العربي", [("2026-11-26 16:00", "AR EP07 بحث", pid(2))])
    posts, _ = cc.parse(md)
    out = cc.source_age(posts, TODAY, episodes=tmp_path)
    assert [(lvl, rule) for lvl, rule, _ in out] == [("warning", "source-age")]
    assert "EP07" in out[0][2] and "2026-11-01" in out[0][2] and "25" in out[0][2]


def test_source_reviewed_recently_is_fine(tmp_path):
    _ep(tmp_path, 7, "2026-11-01")
    md = channel_table("إنستغرام العربي", [("2026-11-10 16:00", "AR EP07 بحث", pid(1))])
    posts, _ = cc.parse(md)
    assert cc.source_age(posts, TODAY, episodes=tmp_path) == []


def test_source_age_uses_the_first_future_post(tmp_path):
    _ep(tmp_path, 7, "2026-11-01")
    md = channel_table("إنستغرام العربي", [("2026-11-10 16:00", "AR EP07 بحث", pid(1))])
    md += channel_table("إنستغرام الإنجليزي", [("2026-11-30 18:00", "EN EP07 Search", pid(2))])
    posts, _ = cc.parse(md)
    assert cc.source_age(posts, TODAY, episodes=tmp_path) == []


def test_past_posts_and_missing_source_are_not_source_age(tmp_path):
    _ep(tmp_path, 7, "2026-10-01")
    (tmp_path / "ep08.md").write_text("# الحلقة 8 — x\n- الحالة: **معتمدة**\n", encoding="utf-8")
    md = channel_table("إنستغرام العربي", [("2026-11-02 16:00", "AR EP07 بحث", pid(1)),
                                           ("2026-12-01 16:00", "AR EP08 x", pid(2))])
    posts, _ = cc.parse(md)
    assert cc.source_age(posts, TODAY, episodes=tmp_path) == []  # missing source = source_check's error


def test_source_age_days_zero_turns_it_off(tmp_path):
    _ep(tmp_path, 7, "2026-10-01")
    md = channel_table("إنستغرام العربي", [("2026-11-26 16:00", "AR EP07 بحث", pid(1))])
    posts, _ = cc.parse(md)
    assert cc.source_age(posts, TODAY, days=0, episodes=tmp_path) == []


def test_plan_rows_get_source_age_too(tmp_path):
    _ep(tmp_path, 7, "2026-11-01")
    rows = [("instagram-ar", dt.datetime(2026, 11, 17, 16), 7),
            ("tiktok-ar", dt.datetime(2026, 11, 19, 16), 7)]
    assert cc.recheck_sources(rows, episodes=tmp_path) == [(7, dt.date(2026, 11, 1), 16)]
    assert cc.recheck_sources(rows, days=20, episodes=tmp_path) == []


# --- now vs today: a post earlier today has already gone out (7 Nov 2026) ---

NOW = dt.datetime(2026, 11, 7, 20, 25)


def test_post_earlier_today_is_past_for_slot_and_weekday():
    # youtube-ar «تحقق قبل أن تثق» went out Saturday 16:00; the 20:25 run still warned "weekday"
    md = channel_table("إنستغرام العربي", [("2026-11-07 16:00", "AR أرشيف", pid(1))])
    assert run(md, today=NOW) == []


def test_post_later_today_is_still_future():
    md = channel_table("إنستغرام العربي", [("2026-11-07 21:00", "AR أرشيف", pid(1))])
    assert ("warning", "weekday") in run(md, today=NOW)


def test_post_earlier_today_counts_as_unconfirmed():
    posts, _ = cc.parse(channel_table("إنستغرام العربي", [("2026-11-07 16:00", "EP01 أ", pid(1))]))
    assert [r for _, r, _ in cc.unconfirmed(posts, NOW)] == ["unconfirmed"]
    assert cc.unconfirmed(posts, NOW.date()) == []  # a date keeps the old whole-day rule


def test_main_now_flag_drives_past_and_future(tmp_path, capsys):
    f = tmp_path / "c.md"
    f.write_text(channel_table("إنستغرام العربي", [("2026-11-07 16:00", "AR أرشيف", pid(1))]), encoding="utf-8")
    assert cc.main(["--file", str(f), "--now", "2026-11-07T20:25", "--runway-days", "0"]) == 0
    out = capsys.readouterr().out
    assert "weekday" not in out and "unconfirmed:" in out
