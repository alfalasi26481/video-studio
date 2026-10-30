#!/usr/bin/env bash
# Step 5 / 7 — Visual QA.
#   bash scripts/check.sh 03 AR stills   -> stills of every scene BEFORE the full render (work/qa/EP03-AR_stills.jpg)
#   bash scripts/check.sh 03 AR final    -> 8 frames sampled from out/EP03-AR.mp4 (work/qa/EP03-AR_final.jpg)
# Look at the contact sheet: cut-off words, overlaps, RTL order, safe zone, timing.
set -euo pipefail
cd "$(dirname "$0")/.."
NN="$1"; L="$2"; MODE="${3:-stills}"; ID="EP${NN}-${L}"
mkdir -p work/qa
if [ "$MODE" = "stills" ]; then
  DUR=$(npx remotion compositions src/index.ts 2>&1 | awk -v id="$ID" '$1==id {print $4}')
  [ -n "$DUR" ] || { echo "composition $ID not found"; exit 1; }
  ins=(); i=0
  for p in 0.05 0.12 0.2 0.3 0.42 0.55 0.68 0.8 0.9 0.97; do
    f=$(python3 -c "print(int($DUR*$p))")
    npx remotion still src/index.ts "$ID" "work/qa/${ID}_$i.png" --frame="$f" --log=error
    ins+=(-i "work/qa/${ID}_$i.png"); i=$((i+1))
  done
  ffmpeg -v error -y "${ins[@]}" -filter_complex "$(for k in $(seq 0 9); do printf "[$k]scale=216:-1[v$k];"; done)[v0][v1][v2][v3][v4][v5][v6][v7][v8][v9]hstack=10" "work/qa/${ID}_stills.jpg"
  echo "work/qa/${ID}_stills.jpg"
else
  N=$(ffprobe -v error -select_streams v -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "out/$ID.mp4")
  sel=$(python3 -c "n=$N; print('+'.join(f'eq(n\\\\,{int(n*p)})' for p in (0.03,0.15,0.3,0.45,0.6,0.72,0.85,0.95)))")
  ffmpeg -v error -y -i "out/$ID.mp4" -vf "select='$sel',scale=225:-1,tile=8x1" -frames:v 1 "work/qa/${ID}_final.jpg"
  echo "work/qa/${ID}_final.jpg"
fi
