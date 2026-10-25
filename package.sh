#!/bin/bash
# Builds a shareable tone-coach.zip (no venv, no key, no profile, no reference audio/video).
K="$(cd "$(dirname "$0")" && pwd)"; OUT="${1:-$PWD/tone-coach.zip}"
cd "$(dirname "$K")" && rm -f "$OUT" && zip -qr "$OUT" tone-coach \
  -x 'tone-coach/.venv/*' 'tone-coach/references/*/audio.*' 'tone-coach/references/*/reel.*' '*/__pycache__/*' '*.DS_Store' \
  && echo "built $OUT" && unzip -l "$OUT" | tail -n +4 | awk '{print $4}' | grep -v '^$'
