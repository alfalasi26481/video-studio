.PHONY: setup clip-status calendar-check calendar-plan cue-check caption-check similarity-check style-check frozen-check frozen-render test validate engine-check glyph-check source-check script-length layout-check check episode episode-preflight episode-kit voice-level
setup:           ## install the Python tools' dependencies (a fresh container lacks brotli for glyph-check)
	python3 -m pip install -q -r requirements-dev.txt $(if $(VIRTUAL_ENV),,--break-system-packages)
test:            ## run all tests
	python3 -m pytest -q
validate:        ## validate every episodes/ep*.yaml
	python3 tools/validate_episode.py --all
engine-check:    ## content rules on master-claude/ episodes (script, captions, on-screen text)
	python3 tools/engine_content_check.py
cue-check:       ## scene cues in speaking order, before voiceDur, on caption lines (3 Nov 2026)
	python3 tools/cue_check.py
caption-check:   ## Arabic caption token glued to a Latin word renders scrambled (EP11, 2 Nov 2026)
	python3 tools/caption_check.py
glyph-check:     ## every on-screen character exists in the engine fonts (all weights)
	python3 tools/glyph_check.py
source-check:    ## every epNN.md cites an official Anthropic page with a review date
	python3 tools/source_check.py
script-length:   ## spoken length of each epNN.md script (estimate before TTS, voiceDur after): 25-35 s, AR≈EN
	python3 tools/script_length.py
layout-check:    ## safe zones + clipped text, measured in Chromium (needs node + playwright)
	python3 tools/layout_check.py
style-check:     ## from EP06: style declared, never the same theme or hook twice in a row, .ts matches .md
	python3 tools/style_check.py
frozen-check:    ## EP01–05 frozen: v1 engine files unchanged, no old episode on engine v2
	python3 tools/frozen_check.py
frozen-render:   ## + render 50 frames of EP01–05 and compare pixels with the approved reference (~3 min)
	python3 tools/frozen_check.py --render
similarity-check: ## no two episodes say the same thing in the same words (owner rule 2 Nov 2026)
	python3 tools/similarity_check.py $(NN)
calendar-check:  ## publishing calendar: no EN on an AR account, no episode twice per channel, no double slot; future posts at 16:00 AR / 18:00 EN, Sun/Tue/Thu; an account's schedule ending within 7 days (warnings)
	python3 tools/calendar_check.py

clip-status:     ## approved episodes still on EP01 placeholder shots + the credits own shots would cost (read-only)
	python3 tools/clip_status.py $(NN)

calendar-plan:  ## read-only: next N (default 3) episodes per account on free Sun/Tue/Thu slots, as rows for CALENDAR.md — schedules nothing
	python3 tools/calendar_check.py --plan $(or $(N),3)
check: validate engine-check cue-check caption-check glyph-check source-check script-length style-check similarity-check calendar-check clip-status frozen-check test
NN ?=
LANGS ?= AR EN
episode:         ## make episode NN=02 [LANGS="AR"] [RENDER=0] [LAYOUT=0] — preflight, checks, render, final QA, hand-off kit in master-claude/out/EPNN/
	@test -n "$(NN)" || (echo "usage: make episode NN=02" && exit 2)
	python3 tools/episode_factory.py preflight $(NN)
	python3 tools/engine_content_check.py $(NN)
	python3 tools/glyph_check.py $(NN)
	python3 tools/source_check.py $(NN)
	python3 tools/cue_check.py $(NN)
	$(if $(filter 0,$(LAYOUT)),@echo "layout check skipped (LAYOUT=0)",python3 tools/layout_check.py $(foreach l,$(LANGS),$(NN)-$(l)))
	python3 tools/episode_factory.py all $(NN) --langs "$(LANGS)" $(if $(filter 0,$(RENDER)),--no-render,)
episode-preflight: ## what is missing for episode NN, and which engine step produces it
	python3 tools/episode_factory.py preflight $(NN)
episode-kit:     ## captions (.srt) + per-platform post text only (no render)
	python3 tools/episode_factory.py kit $(NN)
voice-level:     ## make voice-level NN=04 [FIX=1] — voice loudness vs reference; FIX=1 repairs when final QA failed on loudness
	@test -n "$(NN)" || (echo "usage: make voice-level NN=04 [FIX=1]" && exit 2)
	python3 tools/voice_level.py master-claude/public/vo/ep$(NN)_ar.wav master-claude/public/vo/ep$(NN)_en.wav $(if $(filter 1,$(FIX)),--fix,)
