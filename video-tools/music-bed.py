"""Shapes a music track into a bed for a reel: trims to length, fades out, and ducks it
under actor moments ("speech": true shots) by DUCK_DB with short ramps.

Usage: python3 music-bed.py <work-folder> <music.wav> <out.wav>
"""
import json
import pathlib
import sys
import wave

import numpy as np

DUCK_DB, RAMP, FADE_OUT, FPS = -20.0, 0.15, 1.5, 30
work = pathlib.Path(sys.argv[1])
props = json.loads((work / "render" / "props.json").read_text())
plan = json.loads((work / "edit-plan.cuts.json").read_text())
total = props["totalFrames"] / FPS

with wave.open(sys.argv[2]) as w:
    sr, ch = w.getframerate(), w.getnchannels()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float).reshape(-1, ch) / 32768
n = int(total * sr)
x = x[:n]
t = np.arange(n) / sr

# actor-moment windows, from the same frame maths as the graphics
frame, windows = 0, []
for shot in plan["shots"]:
    if "photo" in shot:
        length = round(shot["dur"] * FPS)
    elif shot.get("move") == "ramp":
        a, b = shot["segments"][0]
        f = (b - a) / 1.2 / 5
        length = round(f * FPS) + round(f / 0.5 * FPS) + round(3 * f * FPS)
    else:
        length = sum(round((e - s) * FPS) for s, e in shot["segments"])
    if shot.get("speech"):
        if windows and abs(windows[-1][1] - frame / FPS) < 1e-6:
            windows[-1][1] = (frame + length) / FPS
        else:
            windows.append([frame / FPS, (frame + length) / FPS])
    frame += length

gain_db = np.zeros(n)
for a, b in windows:
    # ramp down before the moment, back up after it
    down = np.clip((t - (a - RAMP)) / RAMP, 0, 1)
    up = np.clip(((b + RAMP) - t) / RAMP, 0, 1)
    gain_db = np.minimum(gain_db, DUCK_DB * np.minimum(down, up))
gain = 10 ** (gain_db / 20)
gain *= np.clip((total - t) / FADE_OUT, 0, 1)  # fade out
y = x * gain[:, None]
with wave.open(sys.argv[3], "wb") as w:
    w.setnchannels(ch)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
print("ducked under", [[round(a, 2), round(b, 2)] for a, b in windows], f"length {total:.2f}s")
