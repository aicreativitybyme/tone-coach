"""Prints pitch (Hz) every 0.1s for a time window, to check a moment Gemini flagged.
Usage: .venv/bin/python trace.py file.wav start end [pitch_floor=120]
Read it as: numbers climbing at the end of a word = voice goes up, falling = goes down, '-' = silence.
"""
import sys, parselmouth, numpy as np
wav, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
floor = float(sys.argv[4]) if len(sys.argv) > 4 else 120
p = parselmouth.Sound(wav).to_pitch(time_step=0.05, pitch_floor=floor, pitch_ceiling=500)
print(" ".join(f"{t:.1f}:{v:.0f}" if v == v else f"{t:.1f}:-" for t in np.arange(a, b, 0.1) for v in [p.get_value_at_time(t)]))
