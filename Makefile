.PHONY: test validate engine-check glyph-check source-check script-length layout-check check episode episode-preflight episode-kit
test:            ## run all tests
	python3 -m pytest -q
validate:        ## validate every episodes/ep*.yaml
	python3 tools/validate_episode.py --all
engine-check:    ## content rules on master-claude/ episodes (script, captions, on-screen text)
	python3 tools/engine_content_check.py
glyph-check:     ## every on-screen character exists in the engine fonts (all weights)
	python3 tools/glyph_check.py
source-check:    ## every epNN.md cites an official Anthropic page with a review date
	python3 tools/source_check.py
script-length:   ## spoken length of each epNN.md script (estimate before TTS, voiceDur after): 25-35 s, AR≈EN
	python3 tools/script_length.py
layout-check:    ## safe zones + clipped text, measured in Chromium (needs node + playwright)
	python3 tools/layout_check.py
check: validate engine-check glyph-check source-check script-length test
NN ?=
LANGS ?= AR EN
episode:         ## make episode NN=02 [LANGS="AR"] [RENDER=0] — preflight, checks, render, final QA, hand-off kit in master-claude/out/EPNN/
	@test -n "$(NN)" || (echo "usage: make episode NN=02" && exit 2)
	python3 tools/episode_factory.py preflight $(NN)
	python3 tools/engine_content_check.py $(NN)
	python3 tools/glyph_check.py $(NN)
	python3 tools/source_check.py $(NN)
	python3 tools/episode_factory.py all $(NN) --langs "$(LANGS)" $(if $(filter 0,$(RENDER)),--no-render,)
episode-preflight: ## what is missing for episode NN, and which engine step produces it
	python3 tools/episode_factory.py preflight $(NN)
episode-kit:     ## captions (.srt) + per-platform post text only (no render)
	python3 tools/episode_factory.py kit $(NN)
