"""Renders the picture edit (no graphics) from an edit plan, using the original camera files.

Reads <work>/edit-plan.cuts.json and writes:
  <work>/render/base.mp4   1080x1920, 30fps, H.264, with per-shot room/actor audio
Moves (Butter Edit): push = 100->105% over the shot; punch = 112% from the 2nd speech piece;
ramp = 100% -> 50% -> 100% (for 120fps sources). Ambient shots keep room sound at -12 dB;
actor-moment shots ("speech": true) keep it at full level.

Usage: python3 render-base.py <work-folder> <raw-folder>
"""
import json
import pathlib
import subprocess
import sys

work, raw = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
plan = json.loads((work / "edit-plan.cuts.json").read_text())
out = work / "render"
(out / "parts").mkdir(parents=True, exist_ok=True)
FPS, W, H = 30, 1080, 1920
COVER = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2"]


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def push_filter(frames, start_zoom=1.0, end_zoom=1.05):
    # pre-scale 10% larger, then zoompan per frame to the output size
    big = f"scale={int(W * 1.1)}:{int(H * 1.1)}:force_original_aspect_ratio=increase,crop={int(W * 1.1)}:{int(H * 1.1)}"
    z = f"{start_zoom}+({end_zoom}-{start_zoom})*on/{max(frames - 1, 1)}"
    return (f"{big},zoompan=z='{z}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"s={W}x{H}:fps={FPS},setsar=1")


def punch_filter():
    return f"{COVER},crop=iw/1.12:ih/1.12,scale={W}:{H},setsar=1"


parts = []
for shot in plan["shots"]:
    gain = "0dB" if shot.get("speech") else "-12dB"
    sid = f"{shot['id']:02d}"
    if "photo" in shot:
        frames = round(shot["dur"] * FPS)
        p = out / "parts" / f"{sid}_0.mp4"
        run(["-loop", "1", "-framerate", str(FPS), "-t", f"{shot['dur']}",
             "-i", str(work / "photos" / f"{shot['photo']}.jpg"),
             "-f", "lavfi", "-t", f"{shot['dur']}", "-i", "anullsrc=r=48000:cl=stereo",
             "-vf", push_filter(frames) if shot.get("move") == "push" else f"{COVER},fps={FPS}",
             "-frames:v", str(frames), "-shortest", *ENC, str(p)])
        parts.append(p)
        continue
    src = raw / f"{shot['clip']}.MOV"
    segs = shot["segments"]
    if shot.get("move") == "ramp":
        # middle fifth plays at 50%, which adds 20%; shorten the source so the shot keeps its length
        a, b = segs[0]
        f = (b - a) / 1.2 / 5
        segs = [[a, a + f, 1.0], [a + f, a + 2 * f, 0.5], [a + 2 * f, a + 5 * f, 1.0]]
    else:
        segs = [[s, e, 1.0] for s, e in segs]
    shot_len = sum((e - s) / sp for s, e, sp in segs)
    for k, (s, e, speed) in enumerate(segs):
        dur = e - s
        frames = round(dur / speed * FPS)
        if shot.get("move") == "push":
            vf = push_filter(frames)
        elif shot.get("move") == "punch" and k >= 1:
            vf = punch_filter() + f",fps={FPS}"
        else:
            vf = f"{COVER},fps={FPS}"
        if speed != 1.0:
            vf = f"setpts=PTS/{speed}," + vf
        fade = min(0.01, dur / 4)
        af = f"volume={gain},afade=t=in:d={fade},afade=t=out:st={max(dur / speed - fade, 0)}:d={fade}"
        if speed != 1.0:
            af = f"atempo={speed}," + af
        p = out / "parts" / f"{sid}_{k}.mp4"
        run(["-ss", f"{s:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
             "-map", "0:v:0", "-map", "0:a:0", "-vf", vf, "-af", af,
             "-frames:v", str(frames), *ENC, str(p)])
        parts.append(p)
    print(f"shot {sid} {shot['clip']}: {len(segs)} piece(s), {shot_len:.2f}s")

listing = out / "parts.txt"
listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
run(["-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(out / "base.mp4")])
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                    str(out / "base.mp4")], capture_output=True, text=True).stdout.strip()
print("base.mp4", d, "s")
