.PHONY: test validate check
test:            ## run all tests
	python3 -m pytest -q
validate:        ## validate every episodes/ep*.yaml
	python3 tools/validate_episode.py --all
check: validate test
