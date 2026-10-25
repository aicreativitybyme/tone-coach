---
name: tone-coach
description: Checks how someone SPEAKS (melody, punch words, pace, energy) in 1 to 3 of their videos or voiceovers, compares it to a reference reel's delivery levels, and gives an averaged level plus simple fixes. Gemini listens to the audio, pitch numbers double-check it. Use when the user says "tone coach", "check my tone", "how do I sound", "my delivery", "compare my yapping", sends their talking videos or voiceover audio and asks how they sound, or sends a reel of someone speaking and asks how their own voice compares. Also use for "mark my script" / "tone marks": adds punch words and ↗ ↘ arrows to a script before filming.
---

# Tone coach

Claude can't hear audio. Gemini can. So: **Gemini listens to each video → Claude checks it against pitch numbers → the results get averaged → Claude writes one short, plain report.**

`$K` = this skill's folder (`~/.claude/skills/tone-coach`). Work in the session scratchpad (or a temp folder) for working files.

## 0. First time

- If `$K/.venv` is missing, or there's no Gemini key (`GEMINI_API_KEY` / `GOOGLE_AI_API_KEY` env var, or `~/.config/tone-coach/key`): tell the user to run the setup themselves in their terminal, because it asks for their key and Claude must never type it in:
  ```bash
  bash ~/.claude/skills/tone-coach/setup.sh
  ```
  Explain in one line that the key is free and that their audio gets sent to Google's Gemini to be listened to.
- Profile: `~/.config/tone-coach/profile.json`. If it's missing, ask for their first name and create it:
  `{"name": "...", "reports_dir": "~/tone-coach-reports", "videos_hint": "", "open_in_pane": true, "history": []}`.
  Use `name` in the report, save reports to `reports_dir`, and look in `videos_hint` (a folder or glob) when they don't name videos.

## 1. Get the clips

Use whatever they send: **1 to 3 clips**. A clip can be:
- a talking-to-camera video
- a voiceover: a video with their voice over b-roll, or an audio file (mp3, m4a, wav)

If they give a folder, take its 3 newest. 1 clip works fine. When they send just 1, mention once that 3 gives a fairer average, then go ahead. Don't make them add more.
It should be only their voice, one speaker. **Raw takes are best.** Edited reels have the pauses cut out, which hides how they really talk.

## 2. Reference

- **Default:** `$K/references/yap-4-ways/` (one sentence said 4 ways: Hurrying / Managed / Musical / Flowing). If `audio.mp3` is missing, run `bash $K/get-reference.sh`. If that fails, keep going, and Gemini uses the written `notes.txt` only.
- **They send a new reference reel:** download it with `yt-dlp` into `$K/references/<slug>/`. Read its levels from video frames (`ffmpeg -vf fps=1,scale=360:-1`, then `tile`), and find where each level starts and ends with `trace.py`. Write `notes.txt` in the same style as the default (source URL on the first line, then level name, timestamps and what the voice does). Make `audio.mp3` and `audio.wav`, and run `measure.py` → `levels.json`.

## 3. Run

```bash
bash $K/scripts/run.sh <work_dir> $K/references/<ref> "<name>" video1 video2 video3
```
This takes about 1 minute per video. For each clip it writes `clipN.gemini.json` and `clipN.measure.json`, then `summary.json` with the averaged result. Free Gemini keys only get Flash models, and busy models are retried automatically. If a clip fails, report the others and say which one failed.

## 4. Check Gemini before trusting it (always)

For each moment you plan to show, turn `time` into seconds and run `$K/.venv/bin/python $K/scripts/trace.py <work_dir>/clipN.wav <t-1> <t+4>`. Rising numbers at the end of a word = the voice goes up, falling = it goes down. **Drop any moment the trace contradicts**, and list it in the footnote. Gemini sometimes gets a moment wrong.
**Edited clip:** if `sounds_edited` is true (or the file is clearly shorter than the raw take, or named *final* or *edited*), put one line at the top of the report: "This one was edited, so speed and pauses come from the edit, not from you. Send the raw take for a fair check." Leave `hurrying` / `dragging` out of its fixes.
**Voiceover with music under it:** the pitch numbers get confused by the music. If Gemini says `background_music: true` for a clip, skip the trace check for that clip, keep Gemini's moments, and say in the footnote that they weren't double-checked. If they have the voice without the music, ask for that file instead: it gives a better check.
`measure.py` only sees whole sentences, so it misses small rises inside them. Never overrule Gemini on the level with those numbers alone.

## 5. Report

Fill in `$K/report-template.md` and save it as `<reports_dir>/TONE-<YYYY-MM-DD>.md`:
- With 1 clip, drop the "Your videos" table and say "(1 video)" instead of "average of N videos". Call them "videos" or "voiceovers" to match what they sent.
- Level bars use `average_match` from `summary.json`, and "YOU ARE HERE" goes on `closest_level_on_average`.
- "The one thing to fix" = `top_problems[0]`. Its fix comes from `$K/fixes.md`, copied word for word.
- Moments: pick 3–4 verified ones, from at least 2 different videos.
- Plain words. No semitones, Hz or "jumpiness". Write in the language the user is talking to you in.
- Then append `{"date", "level", "top_problem", "videos"}` to `history` in the profile. If there was an earlier entry, add the "Last time → now" line.

Open the report (in the side pane, if `open_in_pane` is on). Reply in 3–4 lines: their level, the one fix, where the file is.

## Mark up a script for filming

When the user says "mark my script", "tone marks", or sends a script they're about to film (also offer this after every report):
- Split each line into short chunks of 2–4 words.
- Put ONE punch word per chunk in **CAPS**.
- Add ↘ at the end of statements, and ↗ ↗ ↘ on lists of three. Use ↗ only where it should pull people into the next line (hook, open loop).
- Follow the fix for their latest `top_problem` from the profile history. Example: `hurrying` → add `/` breath marks, `monotone` → mark the high and low moments.
- Keep their exact words. Don't rewrite the script.
- Save it next to the script as `<name>-TONE.md` and open it.

Example:
```
So / what's the DIFFERENCE ↗ / between Claude and Claude CODE ↘
Aren't they the SAME thing ↗
NOT really ↘
```

## Sharing this skill

`bash $K/package.sh` builds `tone-coach.zip` without the private parts (no `.venv`, key, profile or reference audio). To install, people unzip it into `~/.claude/skills/` and run `setup.sh`. Instructions are in `README.md`.
