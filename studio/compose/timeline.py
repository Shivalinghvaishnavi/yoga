"""Compile a workout script (JSON) into a frame-exact timeline: video loops, speech track, overlay segments."""
import json
import math
import os
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tts"))
from engine import MacSay  # noqa: E402

IDLE_PERIOD = 4.0
WORDS = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen".split()


class Timeline:
    def __init__(self, script_path):
        self.cfg = json.load(open(script_path))
        v = self.cfg["voice"]
        self.tts = MacSay(v["voice"], v["rate"])
        self.t = 0.0
        self.video, self.speech, self.overlay = [], [], []   # video: (clip, loops)

    def say(self, at, text):
        wav, d = self.tts.synth(text)
        self.speech.append((at, wav, d))
        return at + d

    def say_seq(self, start, lines, gap=0.45):
        end = start
        for ln in lines:
            end = self.say(end + gap, ln)
        return end

    def clip(self, name, period, seconds):
        loops = max(1, math.ceil(seconds / period - 1e-9))
        self.video.append((name, loops))
        return loops * period

    def seg(self, kind, name, dur, **kw):
        self.overlay.append(dict(kind=kind, name=name, start=self.t, end=self.t + dur, **kw))
        self.t += dur

    # -- segment types ----------------------------------------------------
    def info(self, s):
        end = self.say_seq(self.t, s["lines"])
        dur = self.clip("idle", IDLE_PERIOD, end - self.t + 0.8)
        self.seg("info", s["name"], dur, next=s.get("next", ""))

    def exercise(self, s):
        p, name = s["period"], s["name"]
        end = self.say_seq(self.t, s["setup_lines"])
        dur = self.clip(s["clip"], p, end - self.t + 0.6)
        self.seg("demo", name, dur, next=s.get("next", ""))
        for k in range(s["sets"]):
            ready = f"Set {k + 1} of {s['sets']}. Ready, and begin."
            e = self.say(self.t + 0.3, ready)
            dur = self.clip("idle", IDLE_PERIOD, e - self.t + 0.5)
            self.seg("ready", name, dur, set=k + 1, sets=s["sets"], reps=s["reps"])
            start, counts = self.t, []
            for r in range(s["reps"]):
                rs = start + r * p
                ct = rs + s["count_at"] * p
                self.say(ct - 0.25, WORDS[r + 1])
                counts.append(ct)
                cue = s.get("cues", {}).get(str(r + 1))
                if cue:
                    self.say(rs + 0.15, cue)
            dur = self.clip(s["clip"], p, s["reps"] * p)
            self.seg("work", name, dur, set=k + 1, sets=s["sets"], reps=s["reps"], counts=counts,
                     next=s.get("next", ""))
            if k < s["sets"] - 1:
                self.say_seq(self.t, s.get("rest_lines", []))
                dur = self.clip("idle", IDLE_PERIOD, s["rest"])
                self.seg("rest", name, dur, set=k + 1, sets=s["sets"], next=s.get("next", ""))

    def timed(self, s):
        p, name = s["period"], s["name"]
        if s.get("setup_lines"):
            end = self.say_seq(self.t, s["setup_lines"])
            dur = self.clip(s["clip"], p, end - self.t + 0.6)
            self.seg("demo", name, dur, next=s.get("next", ""))
        start = self.t
        for sec, text in s.get("cues", {}).items():
            self.say(start + float(sec), text)
        dur = self.clip(s["clip"], p, s["seconds"])
        self.seg("timed", name, dur, next=s.get("next", ""))

    def build(self):
        for s in self.cfg["segments"]:
            getattr(self, "info" if s["type"] in ("intro", "info", "relax") else s["type"])(s)
        self.total = self.t
        return self

    # -- outputs ----------------------------------------------------------
    def write_audio(self, path, sr=44100):
        items = sorted(self.speech)
        out, pos = bytearray(), 0
        for at, wav, d in items:
            f = int(at * sr)
            if f < pos:                       # overlap: push later rather than mix
                print(f"WARN speech overlap {at:.2f}s pushed by {(pos - f) / sr:.2f}s")
                f = pos
            out += b"\x00\x00" * (f - pos)
            with wave.open(wav) as w:
                out += w.readframes(w.getnframes())
            pos = len(out) // 2
        out += b"\x00\x00" * max(0, int(self.total * sr) - pos)
        with wave.open(path, "wb") as w:
            w.setnchannels(1), w.setsampwidth(2), w.setframerate(sr)
            w.writeframes(bytes(out))

    def write_concat(self, path, clip_paths):
        with open(path, "w") as f:
            for name, loops in self.video:
                f.write((f"file '{clip_paths[name]}'\n") * loops)
