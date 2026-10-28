#!/bin/bash
# Render every episode passed as args, both languages, then the QA gate with contact sheets.
cd "$(dirname "$0")/.."
for e in "$@"; do
  for l in ar en; do
    npx remotion render src/index.ts Episode-$l out/$e-$l.mp4 --props="{\"id\":\"$e\",\"lang\":\"$l\"}" --timeout=120000 --crf=18 --log=error && echo "rendered $e-$l"
  done
  python3 scripts/qa.py $e --video out/$e-ar.mp4 --video out/$e-en.mp4 2>/dev/null | tail -4
done
