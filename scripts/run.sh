#!/bin/bash
# Checks 1 or more videos / voiceover audio files (mp4, mov, mp3, m4a, wav...) against a reference.
# With more than one, the results get averaged.
# Usage: run.sh <out_dir> <reference_dir> <speaker name> file1 [file2 file3 ...]
# Writes per clip: clipN.gemini.json, clipN.measure.json. Then summary.json (the average).
set -u
K="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$1"; REF="$2"; NAME="$3"; shift 3
mkdir -p "$OUT"
REFAUDIO="$REF/audio.mp3"; [ -f "$REFAUDIO" ] || REFAUDIO="-"
[ "$REFAUDIO" = "-" ] && echo "No reference audio found, Gemini will use the written description only (run get-reference.sh to fix)."
n=0
for v in "$@"; do
  n=$((n+1)); c="$OUT/clip$n"
  echo "[$n/$#] $(basename "$v")"
  echo "$v" > "$c.source"
  ffmpeg -loglevel error -y -i "$v" -vn -ac 1 -ar 16000 "$c.wav" || { echo "  could not read audio, skipped"; continue; }
  ffmpeg -loglevel error -y -i "$v" -vn -ac 1 -b:a 64k "$c.mp3"
  "$K/.venv/bin/python" "$K/scripts/measure.py" "clip$n,$c.wav,0,end,auto" > "$c.measure.json" || echo "  measuring failed"
  node "$K/scripts/listen.mjs" "$REFAUDIO" "$c.mp3" "$REF/notes.txt" "$K/fixes.md" "$NAME" > "$c.gemini.json" 2> "$c.gemini.log" \
    && echo "  Gemini listened" || echo "  Gemini failed: $(tail -1 "$c.gemini.log")"
done
"$K/.venv/bin/python" "$K/scripts/aggregate.py" "$OUT" > "$OUT/summary.json" && echo "done: $OUT/summary.json"
