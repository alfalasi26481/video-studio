#!/usr/bin/env bash
# Step 6 — Render + master one episode in both languages (approved settings; do not change).
#   bash scripts/render.sh 03            -> out/EP03-AR.mp4, out/EP03-EN.mp4
#   bash scripts/render.sh 03 AR         -> Arabic only
set -euo pipefail
cd "$(dirname "$0")/.."
NN="$1"; LANGS="${2:-AR EN}"
mkdir -p out out/raw
for L in $LANGS; do
  ID="EP${NN}-${L}"
  npx remotion render src/index.ts "$ID" "out/raw/$ID.mp4" \
    --codec=h264 --crf=17 --x264-preset=veryfast --audio-bitrate=192k \
    --concurrency="$(nproc)" --timeout=120000 --log=error
  ffmpeg -v error -y -i "out/raw/$ID.mp4" -c:v copy \
    -af "loudnorm=I=-14:TP=-1.5:LRA=9" -ar 48000 -c:a aac -b:a 192k -movflags +faststart "out/$ID.mp4"
  echo "== $ID  $(ffprobe -v error -show_entries format=duration -of csv=p=0 "out/$ID.mp4")s"
  ffmpeg -hide_banner -i "out/$ID.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tail -2
done
