.PHONY: test validate engine-check check
test:            ## run all tests
	python3 -m pytest -q
validate:        ## validate every episodes/ep*.yaml
	python3 tools/validate_episode.py --all
engine-check:    ## content rules on master-claude/ episodes (script, captions, on-screen text)
	python3 tools/engine_content_check.py
check: validate engine-check test
