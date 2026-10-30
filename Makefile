.PHONY: test validate engine-check glyph-check check
test:            ## run all tests
	python3 -m pytest -q
validate:        ## validate every episodes/ep*.yaml
	python3 tools/validate_episode.py --all
engine-check:    ## content rules on master-claude/ episodes (script, captions, on-screen text)
	python3 tools/engine_content_check.py
glyph-check:     ## every on-screen character exists in the engine fonts (all weights)
	python3 tools/glyph_check.py
check: validate engine-check glyph-check test
