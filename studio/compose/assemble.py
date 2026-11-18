"""Assemble a workout video: render missing motion clips, compile timeline, overlay + voice -> MP4.

  .venv/bin/python studio/compose/assemble.py studio/workouts/day1_test.json out.mp4 [WxH] [camera]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(HERE)
ROOT = os.path.dirname(STUDIO)
sys.path.insert(0, HERE)
from timeline import Timeline  # noqa: E402
from overlay import Overlay  # noqa: E402

BLEND = os.path.join(STUDIO, "character", "instructor_mpfb.blend")


def ensure_clips(names, res, cam):
    d = os.path.join(ROOT, "build", "clips", f"{res}_{cam}")
    os.makedirs(d, exist_ok=True)
    paths = {}
    for n in sorted(set(names)):
        p = os.path.join(d, n + ".mp4")
        if not os.path.exists(p):
            subprocess.check_call(["blender", "-b", BLEND, "-P", os.path.join(STUDIO, "render", "clip_render.py"),
                                   "--", n, cam, p, res], stdout=subprocess.DEVNULL)
        paths[n] = p
    return paths


def main(script, out, res="960x540", cam="front34"):
    W, H = (int(v) for v in res.split("x"))
    tl = Timeline(script).build()
    paths = ensure_clips([c for c, _ in tl.video], res, cam)
    work = os.path.join(ROOT, "build", "work")
    os.makedirs(work, exist_ok=True)
    wav, lst = os.path.join(work, "voice.wav"), os.path.join(work, "concat.txt")
    tl.write_audio(wav)
    tl.write_concat(lst, paths)
    ov = Overlay(tl, W, H)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-i", wav,
           "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
           "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
           "-c:a", "aac", "-b:a", "160k", "-shortest", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(int(round(tl.total * 30))):
            p.stdin.write(ov.frame(i / 30.0))
    except BrokenPipeError:
        pass
    p.stdin.close()
    p.wait()
    print("VIDEO", out, f"{tl.total:.1f}s", "speech lines:", len(tl.speech))


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], *(a[3:5]))
