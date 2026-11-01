"""Makes a 5-frame overview strip per proxy clip: strips/<clip>.jpg.
Usage: python3 clip-strips.py <work-folder>
"""
import pathlib
import subprocess
import sys

work = pathlib.Path(sys.argv[1])
(work / "strips").mkdir(exist_ok=True)
for p in sorted(q for q in (work / "proxies").glob("*.mp4") if ".tmp" not in q.name):
    out = work / "strips" / (p.stem + ".jpg")
    if out.exists():
        continue
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)
    ts = [d * k for k in (0.05, 0.28, 0.5, 0.72, 0.95)]
    args, f = [], ""
    for i, t in enumerate(ts):
        args += ["-ss", f"{t:.2f}", "-i", str(p)]
        label = f"{p.stem[4:]} {t:.1f}s/{d:.1f}s" if i == 0 else f"{t:.1f}s"
        f += (f"[{i}:v]scale=150:266,setsar=1,drawtext=text='{label}':x=2:y=2:fontsize=13:"
              f"fontcolor=yellow:box=1:boxcolor=black@0.7[v{i}];")
    f += "".join(f"[v{i}]" for i in range(5)) + "hstack=5[o]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", f, "-map", "[o]",
                    "-frames:v", "1", str(out)], check=True)
    print("strip", p.stem)
