#!/bin/bash
# One-time setup for tone-coach. Run: bash ~/.claude/skills/tone-coach/setup.sh
K="$(cd "$(dirname "$0")" && pwd)"
ok=1
need() { command -v "$1" >/dev/null || { echo "MISSING: $1  ->  $2"; ok=0; }; }
need ffmpeg  "brew install ffmpeg"
need yt-dlp  "brew install yt-dlp"
need node    "brew install node"
need python3 "brew install python"
[ $ok = 1 ] || { echo; echo "Install the missing tools above (needs Homebrew: https://brew.sh), then run setup again."; exit 1; }

echo "Setting up the voice analysis tools..."
python3 -m venv "$K/.venv" && "$K/.venv/bin/pip" install -q --disable-pip-version-check praat-parselmouth numpy || { echo "Python setup failed"; exit 1; }

KEYF="$HOME/.config/tone-coach/key"
if [ -n "${GEMINI_API_KEY:-}${GOOGLE_AI_API_KEY:-}" ] || [ -s "$KEYF" ]; then
  echo "Gemini key: found"
else
  echo
  echo "tone-coach needs a free Gemini key (Gemini is the part that actually listens)."
  echo "1. Open https://aistudio.google.com/apikey  2. Click 'Create API key'  3. Copy it"
  read -rsp "Paste your key here (it stays hidden) and press Enter: " key; echo
  mkdir -p "$(dirname "$KEYF")" && printf '%s' "$key" > "$KEYF" && chmod 600 "$KEYF" && echo "Key saved to $KEYF"
fi

bash "$K/get-reference.sh"
echo
echo "Done. In Claude Code, say: \"tone coach\" and give it 3 of your videos."
