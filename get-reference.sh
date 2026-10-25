#!/bin/bash
# Downloads the default reference reel's audio (it is not shipped with the skill, it belongs to its creator).
K="$(cd "$(dirname "$0")" && pwd)"; R="$K/references/yap-4-ways"
URL=$(grep -m1 -o 'https://[^ ]*' "$R/notes.txt")
cd "$R" && yt-dlp -q --no-warnings -o "reel.%(ext)s" -f mp4 "$URL" && ffmpeg -loglevel error -y -i reel.mp4 -vn -ac 1 -b:a 64k audio.mp3 && ffmpeg -loglevel error -y -i reel.mp4 -vn -ac 1 -ar 16000 audio.wav && rm -f reel.mp4 && echo "reference ready" || echo "Could not download the reference. The skill still works, using the written description of it."
