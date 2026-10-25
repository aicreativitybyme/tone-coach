"""Averages the per-clip results in an output folder into one summary. Prints JSON.
Usage: python aggregate.py <out_dir>
"""
import sys, json, glob, os, re
from collections import Counter, defaultdict

out = sys.argv[1]


def level_key(name):
    """Gemini writes level names a bit differently each time ('Level 2: Better / Managed', '2 "Better/Managed"').
    Normalise to '<number> <name>' so the same level averages together."""
    n = re.search(r"\d", name or "")
    words = re.sub(r"(?i)level|\d|[:\"'()]", " ", name or "").split()
    return f"{n.group() if n else '?'} {' '.join(words)}".replace(" / ", "/").strip()

clips, levels, problems, strengths, moments, nums = [], defaultdict(list), Counter(), Counter(), [], defaultdict(list)
for g in sorted(glob.glob(os.path.join(out, "clip*.gemini.json"))):
    clip = os.path.basename(g).split(".")[0]
    try:
        r = json.load(open(g))
    except Exception:
        continue
    src = open(os.path.join(out, clip + ".source")).read().strip()
    clips.append({"clip": clip, "file": src, "closest_level": level_key(r.get("closest_level")), "main_gap": r.get("main_gap"), "energy": r.get("energy"),
                  "kind": r.get("kind"), "background_music": r.get("background_music"),
                  "sounds_edited": r.get("sounds_edited")})
    for l in r.get("per_level", []):
        levels[level_key(l["level"])].append(l["match"])
    for i, p in enumerate(r.get("problems", [])[:3]):
        problems[p] += 3 - i  # first-named problem counts most
    strengths.update(s.strip().rstrip(".") for s in r.get("strengths", []))
    moments += [dict(m, clip=clip, file=os.path.basename(src)) for m in r.get("moments", [])]
    m = os.path.join(out, clip + ".measure.json")
    if os.path.exists(m):
        for k, v in json.load(open(m))[clip].items():
            if isinstance(v, (int, float)): nums[k].append(v)

# merge by level number (names may still differ slightly), keep the first name seen
merged = {}
for l, v in levels.items():
    num = l.split()[0]
    k = next((m for m in merged if m.split()[0] == num), l)
    merged.setdefault(k, []).extend(v)
avg = {l: round(sum(v) / len(v), 1) for l, v in merged.items()}
print(json.dumps({
    "clips_checked": len(clips),
    "average_match": dict(sorted(avg.items())),
    "closest_level_on_average": max(avg, key=avg.get) if avg else None,
    "per_clip": clips,
    "top_problems": [p for p, _ in problems.most_common(3)],
    "problem_scores": dict(problems.most_common()),
    "strengths_mentioned": [s for s, _ in strengths.most_common(6)],
    "moments": moments,
    "average_numbers": {k: round(sum(v) / len(v), 2) for k, v in nums.items()},
}, indent=1, ensure_ascii=False))
