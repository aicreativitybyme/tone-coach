// Sends a reference reel's audio + one of the speaker's clips to Gemini (which can actually hear audio)
// and asks for a tone comparison. Prints JSON to stdout.
// Usage: node listen.mjs <reference.mp3 or -> <clip.mp3> <reference-notes.txt> <fixes.md> [speaker name]
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [refPath, clipPath, notesPath, fixesPath, name = "the speaker"] = process.argv.slice(2);
const keyFile = path.join(os.homedir(), ".config", "tone-coach", "key");
const key = process.env.GEMINI_API_KEY || process.env.GOOGLE_AI_API_KEY ||
  (fs.existsSync(keyFile) ? fs.readFileSync(keyFile, "utf8").trim() : "");
if (!key) { console.error("No Gemini key. Run setup.sh first."); process.exit(1); }

const notes = fs.readFileSync(notesPath, "utf8");
const fixes = fs.readFileSync(fixesPath, "utf8");
const problemIds = [...fixes.matchAll(/^## (\S+)/gm)].map((m) => m[1]);
const problems = [...fixes.matchAll(/^## (\S+)\n\*\*Problem:\*\* (.+)$/gm)].map((m) => `- ${m[1]}: ${m[2]}`).join("\n");
const audio = (p) => ({ inline_data: { mime_type: "audio/mp3", data: fs.readFileSync(p).toString("base64") } });
const hasRef = refPath && refPath !== "-" && fs.existsSync(refPath);

const prompt = `You are a voice and delivery coach for short videos (Instagram Reels, TikTok, Shorts).
The speaker's clip may be talking to camera OR a voiceover (recorded voice, maybe with music under it). Judge only the voice either way. If the clip sounds edited (jump cuts, pauses removed, sped up), do NOT blame the speaker for hurrying or missing pauses. For a voiceover, keep in mind it has no face or hands to help, so the voice has to do all the work.
${hasRef ? "AUDIO 1 is a REFERENCE clip." : "There is no reference audio, only this description of a reference clip."} What it demonstrates:
${notes}

${hasRef ? "AUDIO 2" : "The audio"} is ${name}. Listen to the DELIVERY (melody, stress, rhythm, pace, energy), not the content.
Compare it to the reference levels. Use the level names exactly as written above, starting with their number. Be honest and specific, not flattering. Use simple English (short sentences, no jargon, they are not a voice professional).

Pick the problems you clearly hear, most important first, ONLY from this list (use the ids):
${problems}

Return ONLY JSON in this shape:
{
  "closest_level": "the name of the reference level they sound most like",
  "closest_level_why": "1-2 sentences",
  "per_level": [{"level": "...", "match": 0-10, "note": "one short sentence"}],
  "problems": ["1-3 ids from the list, most important first"],
  "strengths": ["max 3 short items"],
  "main_gap": "the ONE biggest thing keeping them from the best level, 1-2 sentences",
  "moments": [{"time": "mm:ss", "quote": "their exact words there (max 10 words)", "what_happens": "what their voice does", "try_instead": "how to say it, mark the punch word in CAPS and use ↗ / ↘ for pitch"}],
  "energy": "one sentence on energy / warmth / confidence as heard",
  "clarity_note": "one sentence, only if pronunciation affects clarity, else empty string",
  "kind": "talking-head or voiceover (your best guess from the audio)",
  "background_music": true or false,
  "sounds_edited": "true if you hear jump cuts, removed pauses or a sped-up voice (then pace/pause problems may come from the edit, not the speaker), else false"
}
Give 3 to 5 moments.`;

const parts = hasRef
  ? [{ text: "AUDIO 1 (reference):" }, audio(refPath), { text: `AUDIO 2 (${name}):` }, audio(clipPath), { text: prompt }]
  : [{ text: `AUDIO (${name}):` }, audio(clipPath), { text: prompt }];

async function ask(model) {
  const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contents: [{ parts }], generationConfig: { temperature: 0.3, responseMimeType: "application/json" } }),
  });
  const j = await r.json();
  if (!r.ok) throw new Error(`${model}: ${j.error?.message || r.status}`);
  const out = JSON.parse(j.candidates[0].content.parts.map((p) => p.text).join(""));
  out.problems = (out.problems || []).filter((id) => problemIds.includes(id));
  out.model = model;
  return out;
}

// Free keys: Pro models have no quota, so Flash first (Pro last, for paid keys). Busy models get 2 more tries.
const models = ["gemini-flash-latest", "gemini-3.8-flash", "gemini-3.5-flash", "gemini-pro-latest"];
let out;
for (let round = 0; round < 3 && !out; round++) {
  for (const m of models) {
    try { out = await ask(m); break; } catch (e) { console.error(e.message.split("\n")[0]); }
  }
  if (!out) await new Promise((r) => setTimeout(r, 20000));
}
if (!out) process.exit(1);
console.log(JSON.stringify(out, null, 1));
