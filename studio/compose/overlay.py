"""Draw on-screen guidance (name, set/rep, timers, progress, next) with Pillow; frames are cached per state."""
import os
from PIL import Image, ImageDraw, ImageFont

TEAL, CORAL, INK = (20, 110, 118), (222, 92, 72), (24, 40, 46)
FONT = "/System/Library/Fonts/Avenir Next.ttc"


def _font(size, bold=False):
    try:
        return ImageFont.truetype(FONT, size, index=1 if bold else 0)
    except Exception:
        return ImageFont.load_default()


def mmss(s):
    s = int(s)
    return f"{s // 60:02d}:{s % 60:02d}"


class Overlay:
    def __init__(self, tl, W, H, fps=30):
        self.tl, self.W, self.H, self.fps, self.cache = tl, W, H, fps, {}
        self.u = H / 1080
        self.f = {k: _font(int(sz * self.u), b) for k, (sz, b) in
                  dict(title=(54, True), big=(120, True), mid=(40, True), small=(32, False)).items()}

    def state(self, t):
        for i, s in enumerate(self.tl.overlay):
            if s["start"] <= t < s["end"]:
                reps = sum(1 for c in s.get("counts", []) if c <= t)
                rest = int(s["end"] - t) + 1 if s["kind"] in ("rest", "timed") else 0
                return i, reps, rest, int(t)
        return len(self.tl.overlay) - 1, 0, 0, int(t)

    def frame(self, t):
        key = self.state(t)
        if key not in self.cache:
            if len(self.cache) > 64:
                self.cache.clear()
            self.cache[key] = self._draw(self.tl.overlay[key[0]], *key[1:], t=t)
        return self.cache[key]

    def _panel(self, d, box, fill=(255, 255, 255, 215), r=24):
        d.rounded_rectangle([int(v * self.u) for v in box], int(r * self.u), fill=fill)

    def _draw(self, s, reps, rest, secs, t):
        W, H, u = self.W, self.H, self.u
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        kind = s["kind"]
        self._panel(d, (40, 36, 760, 172))
        d.text((int(70 * u), int(52 * u)), s["name"], font=self.f["title"], fill=INK)
        tag = {"demo": "WATCH THE DEMO", "ready": "GET READY", "work": "KEEP GOING", "rest": "REST", "info": "", "timed": "KEEP GOING"}[kind]
        if tag:
            d.text((int(70 * u), int(122 * u)), tag, font=self.f["small"], fill=CORAL)
        if "set" in s:
            self._panel(d, (1560, 36, 1880, 120))
            d.text((int(1590 * u), int(52 * u)), f"Set {s['set']} of {s['sets']}", font=self.f["mid"], fill=TEAL)
        if kind == "work":
            self._panel(d, (40, 700, 420, 940))
            d.text((int(70 * u), int(716 * u)), "REPS", font=self.f["small"], fill=TEAL)
            d.text((int(70 * u), int(760 * u)), f"{reps}", font=self.f["big"], fill=INK)
            d.text((int(260 * u), int(840 * u)), f"/ {s['reps']}", font=self.f["mid"], fill=TEAL)
        if kind == "timed":
            left = int(s["end"] - t) + 1
            self._panel(d, (40, 700, 420, 940))
            d.text((int(70 * u), int(716 * u)), "TIME", font=self.f["small"], fill=TEAL)
            d.text((int(70 * u), int(760 * u)), f"{left}", font=self.f["big"], fill=INK)
        if kind == "rest":
            self._panel(d, (1500, 380, 1880, 640), fill=(222, 92, 72, 225))
            d.text((int(1530 * u), int(398 * u)), "REST", font=self.f["small"], fill=(255, 255, 255))
            d.text((int(1530 * u), int(440 * u)), f"{rest}", font=self.f["big"], fill=(255, 255, 255))
        if s.get("next") and kind in ("work", "rest", "demo", "timed"):
            self._panel(d, (1340, 860, 1880, 940))
            d.text((int(1370 * u), int(876 * u)), f"Next: {s['next']}", font=self.f["small"], fill=INK)
        # bottom bar: elapsed / total + progress
        self._panel(d, (40, 980, 1880, 1050), r=14)
        d.text((int(70 * u), int(992 * u)), f"{mmss(t)} / {mmss(self.tl.total)}", font=self.f["small"], fill=INK)
        x0, x1, y0, y1 = [int(v * u) for v in (360, 1840, 1004, 1026)]
        d.rounded_rectangle([x0, y0, x1, y1], int(11 * u), fill=(205, 215, 215, 255))
        d.rounded_rectangle([x0, y0, x0 + max(int(22 * u), int((x1 - x0) * t / self.tl.total)), y1], int(11 * u), fill=TEAL)
        return im.tobytes()
