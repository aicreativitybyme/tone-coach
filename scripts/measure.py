"""Measures delivery numbers for one or more audio sections. Prints JSON.
Usage: .venv/bin/python measure.py "label,file.wav,start,end,pitch_floor" ...
pitch_floor: 70 for a lower voice, 120 for a higher voice, or "auto" to detect it.
"""
import sys, json, parselmouth, numpy as np


def split(tv, talking, min_gap):
    """Speech stretches separated by pauses of at least min_gap frames (10ms each)."""
    out, start, gap, end = [], None, 0, None
    for t, x in zip(tv, talking):
        if x:
            start = t if start is None else start
            gap, end = 0, t
        elif start is not None:
            gap += 1
            if gap >= min_gap:
                out.append((start, end)); start = None
    if start is not None:
        out.append((start, end))
    return out


def ending(tp, f, med, a, b, min_frames):
    sel = (tp >= a) & (tp <= b) & (f > 0)
    x = 12 * np.log2(f[sel] / med)
    x = x[np.abs(x) < 12]  # drop octave errors
    if len(x) < min_frames:
        return None, None
    n = max(3, len(x) // 4)
    return x, np.median(x[-n:]) - np.median(x[:n])


def measure(wav, a, b, floor):
    s = parselmouth.Sound(wav).extract_part(a, b)
    it = s.to_intensity(time_step=0.01)
    v, tv = it.values[0], it.xs()
    talking = v > np.percentile(v, 90) - 18
    p = s.to_pitch(time_step=0.01, pitch_floor=floor, pitch_ceiling=500)
    f, tp = p.selected_array["frequency"], p.xs()
    med = np.median(f[f > 0])

    # sentences = speech between pauses of 250ms+. Short in-sentence rises are NOT caught here,
    # that is what the Gemini listen and the pitch trace (trace.py) are for.
    ranges, jumps, endings = [], [], []
    for a2, b2 in split(tv, talking, 25):
        x, d = ending(tp, f, med, a2, b2, 15)
        if x is None:
            continue
        ranges.append(np.percentile(x, 95) - np.percentile(x, 5))
        jumps.append(np.std(np.diff(x[::5])))
        endings.append(d)

    # talk runs between short pauses (120ms+)
    runs, cur, n = [], talking[0], 0
    for x in talking:
        if x == cur: n += 1
        else: runs.append((cur, n)); cur, n = x, 1
    runs.append((cur, n))
    talk_runs = [n / 100 for c, n in runs if c]
    e = np.array(endings)
    return {
        "pitch_range_semitones": round(float(np.median(ranges)), 1),
        "jumpiness": round(float(np.median(jumps)), 2),
        "sentence_endings_down_pct": round(float(np.mean(e < -1.5) * 100)),
        "sentence_endings_level_pct": round(float(np.mean(abs(e) <= 1.5) * 100)),
        "sentence_endings_up_pct": round(float(np.mean(e > 1.5) * 100)),
        "longest_talk_run_sec": round(max(talk_runs), 1),
        "phrases": len(ranges),
    }


def detect_floor(wav):
    """Higher voices need a higher pitch floor or the tracker finds fake low notes."""
    f = parselmouth.Sound(wav).to_pitch(pitch_floor=75, pitch_ceiling=500).selected_array["frequency"]
    return 120.0 if np.median(f[f > 0]) > 165 else 70.0


out = {}
for spec in sys.argv[1:]:
    label, wav, a, b, floor = spec.split(",")
    floor = detect_floor(wav) if floor == "auto" else float(floor)
    b = float(b) if b != "end" else parselmouth.Sound(wav).duration
    out[label] = measure(wav, float(a), b, floor)
    out[label]["voice"] = "higher" if floor > 100 else "lower"
print(json.dumps(out, indent=1))
