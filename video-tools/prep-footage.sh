#!/usr/bin/env bash
# Prepares raw iPhone clips for editing:
#   proxies/<clip>.mp4       1080-wide H.264 working copy (rotation applied)
#   audio/<clip>.wav         16 kHz mono for Whisper
#   transcripts/<clip>.json  Whisper transcript with word timings
#   sheets/<clip>.jpg        contact sheet (2 frames per second)
# Usage: prep-footage.sh <raw-folder> <work-folder> [parallel-jobs]
# Safe to re-run: finished outputs are skipped, partial ones are redone.
set -euo pipefail
RAW="$1"; WORK="$2"; JOBS="${3:-3}"
mkdir -p "$WORK"/{proxies,audio,transcripts,sheets}

prep_one() {
  src="$1"; WORK="$2"
  W="$HOME/video-tools/whisper.cpp"
  name=$(basename "${src%.*}")
  if [ ! -s "$WORK/proxies/$name.mp4" ]; then
    ffmpeg -v error -y -i "$src" -map 0:v:0 -map 0:a:0? \
      -vf "scale='if(gt(iw,ih),1920,1080)':-2,format=yuv420p" \
      -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 192k -movflags +faststart \
      "$WORK/proxies/$name.tmp.mp4" && mv "$WORK/proxies/$name.tmp.mp4" "$WORK/proxies/$name.mp4"
  fi
  if [ ! -s "$WORK/audio/$name.wav" ]; then
    ffmpeg -v error -y -i "$src" -vn -ar 16000 -ac 1 "$WORK/audio/$name.tmp.wav" \
      && mv "$WORK/audio/$name.tmp.wav" "$WORK/audio/$name.wav" || true
  fi
  if [ -s "$WORK/audio/$name.wav" ] && [ ! -s "$WORK/transcripts/$name.json" ]; then
    "$W/build/bin/whisper-cli" -m "$W/models/ggml-base.en.bin" -t 2 -f "$WORK/audio/$name.wav" \
      -np -ojf -of "$WORK/transcripts/$name" >/dev/null 2>&1 || true
  fi
  if [ ! -s "$WORK/sheets/$name.jpg" ]; then
    ffmpeg -v error -y -i "$WORK/proxies/$name.mp4" \
      -vf "fps=2,scale=180:-1,drawtext=text='$name %{pts\:hms}':x=3:y=3:fontsize=12:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=8x4" \
      -frames:v 1 "$WORK/sheets/$name.jpg"
  fi
  echo "done $name"
}
export -f prep_one

rm -f "$WORK"/proxies/*.tmp.mp4 "$WORK"/audio/*.tmp.wav
find "$RAW" -maxdepth 1 -type f \( -iname '*.mov' -o -iname '*.mp4' \) -print0 | sort -z \
  | xargs -0 -P "$JOBS" -I{} bash -c 'prep_one "$1" "$2"' _ {} "$WORK"
