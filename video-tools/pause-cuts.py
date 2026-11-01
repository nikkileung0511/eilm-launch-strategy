"""Computes pause cuts for speech shots in an edit plan.

Only shots marked "speech": true are touched; ambient shots keep their full length.
Inside a speech shot, a 20 ms frame counts as speech if either
  * Silero VAD marked it as speech (vad/<clip>.txt, from whisper-vad-speech-segments), or
  * its loudness is at least LOUD_DB above that clip's background level (20th percentile).
Non-speech runs longer than MAX_GAP are removed, keeping PAD either side of speech.

Usage: python3 pause-cuts.py <work-folder>   -> writes <work-folder>/edit-plan.cuts.json
"""
import json
import pathlib
import re
import sys
import wave

import numpy as np

MAX_GAP = 0.10
PAD = 0.04
LOUD_DB = 8.0
HOP = 0.02

work = pathlib.Path(sys.argv[1])
plan = json.loads((work / "edit-plan.json").read_text())


def speech_mask(clip):
    with wave.open(str(work / "audio" / f"{clip}.wav")) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float) / 32768
    hop = int(HOP * sr)
    frames = len(x) // hop
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) + 1e-9)
                   for i in range(frames)])
    mask = db >= np.percentile(db, 20) + LOUD_DB
    vad = work / "vad" / f"{clip}.txt"
    if vad.exists():
        for line in vad.read_text().splitlines():
            m = re.search(r"start = ([\d.]+), end = ([\d.]+)", line)
            if m:  # VAD reports hundredths of a second
                s, e = float(m.group(1)) / 100, float(m.group(2)) / 100
                mask[int(s / HOP):int(e / HOP) + 1] = True
    # safety net: protect the onset of every word Whisper heard (words/<clip>.json, -ml 1)
    words = work / "words" / f"{clip}.json"
    if words.exists():
        for seg in json.loads(words.read_text())["transcription"]:
            text = seg["text"].strip()
            if text and not re.match(r"^[\(\[\-]", text):
                s = seg["offsets"]["from"] / 1000
                mask[max(0, int((s - 0.05) / HOP)):int((s + 0.25) / HOP) + 1] = True
    return mask


total_before = total_after = 0.0
for shot in plan["shots"]:
    if "clip" not in shot:
        shot["segments"] = []
        total_before += shot["dur"]
        total_after += shot["dur"]
        continue
    a, b = shot["in"], shot["out"]
    total_before += b - a
    if not shot.get("speech"):
        shot["segments"] = [[a, b]]
        total_after += b - a
        continue
    mask = speech_mask(shot["clip"])
    i0, i1 = int(a / HOP), min(int(b / HOP), len(mask))
    # find speech runs inside [a, b]
    runs, start = [], None
    for i in range(i0, i1):
        if mask[i] and start is None:
            start = i
        if (not mask[i] or i == i1 - 1) and start is not None:
            end = i + 1 if mask[i] else i
            runs.append([start * HOP, end * HOP])
            start = None
    # pad, clamp, merge gaps that are short enough to keep
    spans = []
    for s, e in runs:
        s, e = max(a, s - PAD), min(b, e + PAD)
        if spans and s - spans[-1][1] <= MAX_GAP:
            spans[-1][1] = max(spans[-1][1], e)
        else:
            spans.append([s, e])
    # drop slivers shorter than 80 ms (clicks, not words)
    spans = [sp for sp in spans if sp[1] - sp[0] >= 0.08] or [[a, b]]
    shot["segments"] = [[round(s, 3), round(e, 3)] for s, e in spans]
    kept = sum(e - s for s, e in shot["segments"])
    total_after += kept
    print(f"shot {shot['id']:>2} {shot['clip']}: {b - a:5.2f}s -> {kept:5.2f}s, "
          f"{len(spans) - 1} pause(s) cut  {shot['segments']}")

plan["duration_before"] = round(total_before, 2)
plan["duration_after"] = round(total_after, 2)
(work / "edit-plan.cuts.json").write_text(json.dumps(plan, indent=1))
print(f"total {total_before:.1f}s -> {total_after:.1f}s")
