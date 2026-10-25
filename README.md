# tone-coach: a Claude Code skill

Find out how you **sound** on camera, not just what you say.
Give it 1 to 3 of your talking videos or voiceovers. It tells you your delivery level (Hurrying → Managed → Musical → Flowing), the ONE thing to fix, the exact moments in your videos, and simple drills.

Claude can't hear audio, so **Gemini listens** to your videos. Pitch measurements double-check what Gemini says.

The 4 levels come from Jun Yuh's (@jun_yuh) "same sentence, 4 ways" reel. Made by Anna, @annagoes.live.

## Install (5 minutes, Mac)

**Easiest:** open Claude Code and say:
> install the tone-coach skill from https://github.com/<this repo> and run its setup

**Or by hand,** in Terminal:
```bash
git clone https://github.com/<this repo>.git ~/.claude/skills/tone-coach
bash ~/.claude/skills/tone-coach/setup.sh
```
Setup checks your tools (ffmpeg, yt-dlp, node, python) and tells you how to install anything missing.
It also asks for a **free Gemini key**: https://aistudio.google.com/apikey → "Create API key".

Then in Claude Code, say **"tone coach"** and give it 1 to 3 raw videos.

Don't use GitHub's "Download ZIP": the folder arrives as `tone-coach-main` and Claude won't find the skill unless you rename it to `tone-coach`.

## Use

- **"tone coach"** + 1 to 3 videos or voiceovers (mp4, mov, mp3, m4a, wav) → your report (saved to `~/tone-coach-reports/`).
- **"mark my script"** + a script → punch words in CAPS and ↗ ↘ arrows, ready to film.
- Record new takes with the fixes, then run "tone coach" again. It shows if you moved up a level.

Tips: use raw takes (edited videos hide your pauses). One speaker. Voiceovers work best without music under them.

## Privacy

Your audio is sent to Google Gemini with **your own key**, so it can be listened to. Nothing is sent anywhere else.
The default reference reel is downloaded from Instagram during setup. It isn't included in this repo.
