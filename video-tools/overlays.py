"""Builds Remotion props (graphics timings) for ButterReel from an edit plan.

Frame counts mirror render-base.py exactly, so graphics land on the cuts.
Also writes captions.srt (burned-in actor captions) and vo-guide.txt (where each voiceover line goes).

Usage: python3 overlays.py <work-folder> <video-path-in-remotion-public>  -> <work>/render/props.json
"""
import json
import pathlib
import sys

FPS = 30
work = pathlib.Path(sys.argv[1])
plan = json.loads((work / "edit-plan.cuts.json").read_text())


def pieces(shot):
    if "photo" in shot:
        return [round(shot["dur"] * FPS)]
    segs = shot["segments"]
    if shot.get("move") == "ramp":
        a, b = segs[0]
        f = (b - a) / 1.2 / 5
        return [round(f * FPS), round(f / 0.5 * FPS), round(3 * f * FPS)]
    return [round((e - s) * FPS) for s, e in segs]


def wrap(text, width=30):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return "\n".join(lines + [line])


overlays, cuts, frame = [], [], 0
starts = {}
for shot in plan["shots"]:
    ps = pieces(shot)
    starts[shot["id"]] = (frame, sum(ps), ps)
    frame += sum(ps)
    cuts.append(frame)
total = frame


def next_cut_after(f):
    return next((c for c in cuts if c >= f), total)


for shot in plan["shots"]:
    start, length, ps = starts[shot["id"]]
    t = shot.get("text", {})
    if "opener" in t:
        o = t["opener"]
        overlays.append({"type": "opener", "from": start, "dur": length, **o})
    if "card" in t:
        plain, italic = t["card"]
        need = 2 * len(plain + italic) + int(1.2 * FPS)  # type-on, then hold at least 1.2s
        end = next_cut_after(start + need)
        overlays.append({"type": "card", "from": start, "dur": end - start, "plain": plain, "italic": italic})
    if "pop" in t:
        overlays.append({"type": "pop", "from": start + 6, "dur": 5 + FPS, "text": t["pop"]})
    if "caption" in t:
        caps = [t["caption"]] if isinstance(t["caption"], str) else t["caption"]
        if len(caps) == 1:
            overlays.append({"type": "caption", "from": start, "dur": length, "text": wrap(caps[0])})
        else:  # first line over the first speech piece, the rest over the remainder
            overlays.append({"type": "caption", "from": start, "dur": ps[0], "text": wrap(caps[0])})
            overlays.append({"type": "caption", "from": start + ps[0], "dur": length - ps[0], "text": wrap(caps[1])})

props = {"video": sys.argv[2], "totalFrames": total, "location": plan["location_tag"], "overlays": overlays}
out = work / "render"
out.mkdir(exist_ok=True)
(out / "props.json").write_text(json.dumps(props, indent=1, ensure_ascii=False))


def ts(f):
    s = f / FPS
    return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round(s % 1 * 1000)) % 1000:03d}"


srt = [f"{k}\n{ts(o['from'])} --> {ts(o['from'] + o['dur'])}\n{o['text']}\n"
       for k, o in enumerate((o for o in overlays if o["type"] == "caption"), 1)]
(out / "captions.srt").write_text("\n".join(srt))

# voiceover guide: each line starts at its section's first shot and runs until the next actor moment / line
guide, vo_shots = [], [s for s in plan["shots"] if "vo" in s]
for k, s in enumerate(vo_shots):
    a = starts[s["id"]][0]
    ids = [x["id"] for x in plan["shots"]]
    i = ids.index(s["id"]) + 1
    while i < len(ids) and plan["shots"][i]["section"] == s["section"]:
        i += 1
    b = starts[ids[i]][0] if i < len(ids) else total
    guide.append(f"{a / FPS:5.1f}s - {b / FPS:5.1f}s  ({(b - a) / FPS:.1f}s)  {s['vo']}")
actor = [f"{starts[s['id']][0] / FPS:5.1f}s - {(starts[s['id']][0] + starts[s['id']][1]) / FPS:5.1f}s  "
         f"ACTOR MOMENT, keep quiet: {' / '.join([s['text']['caption']] if isinstance(s.get('text', {}).get('caption'), str) else s.get('text', {}).get('caption') or [s.get('text', {}).get('pop', '')])}"
         for s in plan["shots"] if s.get("speech")]
lines = sorted(guide + actor, key=lambda x: float(x.split("s")[0]))
(out / "vo-guide.txt").write_text(
    "Voiceover guide: where each line of your script goes in the reel\n"
    "Read at your normal pace; each window was sized at about 3.3 words per second.\n\n" + "\n".join(lines) + "\n")
print(f"{len(overlays)} graphics, {total} frames ({total / FPS:.2f}s)")
