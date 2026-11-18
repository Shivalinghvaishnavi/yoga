"""Pluggable text-to-speech. Swap `MacSay` for another class with the same `synth` signature later."""
import hashlib
import json
import os
import subprocess

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")


def duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "json", path])
    return float(json.loads(out)["format"]["duration"])


class MacSay:
    """macOS built-in voices via `say` (free, offline). Output: 44.1 kHz mono WAV, cached by text+voice."""
    name = "macsay"

    def __init__(self, voice="Samantha", rate=165):
        self.voice, self.rate = voice, rate

    def synth(self, text, out_path=None):
        os.makedirs(CACHE, exist_ok=True)
        key = hashlib.sha1(f"{self.name}|{self.voice}|{self.rate}|{text}".encode()).hexdigest()[:16]
        wav = out_path or os.path.join(CACHE, key + ".wav")
        if os.path.exists(wav):
            return wav, duration(wav)
        tmp = wav + ".aiff"
        subprocess.check_call(["say", "-v", self.voice, "-r", str(self.rate), "-o", tmp, text])
        subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ar", "44100", "-ac", "1", wav])
        os.remove(tmp)
        return wav, duration(wav)
