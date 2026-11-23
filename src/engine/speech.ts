const PREFERRED = ['Samantha', 'Karen', 'Tara', 'Flo', 'Shelley', 'Sandy', 'Google UK English Female']

export function pickVoice(): SpeechSynthesisVoice | null {
  if (typeof speechSynthesis === 'undefined') return null
  const en = speechSynthesis.getVoices().filter((v) => v.lang.toLowerCase().startsWith('en'))
  // Voices that run on the device are preferred: network voices can silently drop short utterances such as counts.
  const local = en.filter((v) => v.localService)
  for (const pool of [local, en]) {
    for (const name of PREFERRED) {
      const hit = pool.find((v) => v.name.startsWith(name))
      if (hit) return hit
    }
  }
  return local[0] ?? en[0] ?? null
}

// Phones and some browsers only allow speech after the page has spoken once from a tap. Call this from a click handler.
export function unlockSpeech() {
  if (typeof speechSynthesis === 'undefined') return
  try {
    const u = new SpeechSynthesisUtterance(' ')
    u.volume = 0
    speechSynthesis.speak(u)
    speechSynthesis.resume()
  } catch { /* nothing to unlock */ }
}

// Speaks one line at a time. Every call to say() cancels whatever came before, so a
// late utterance from an old step can never play over the new one.
export class Speaker {
  volume = 1
  muted = false
  voice: SpeechSynthesisVoice | null = null
  onCaption: (text: string) => void = () => {}
  private gen = 0
  private fallback: ReturnType<typeof setTimeout> | null = null

  cancel() {
    this.gen++
    if (this.fallback) clearTimeout(this.fallback)
    if (typeof speechSynthesis !== 'undefined') speechSynthesis.cancel()
  }

  // Muting silences the line being spoken right now; captions and pacing continue.
  setMuted(m: boolean) {
    this.muted = m
    if (m && typeof speechSynthesis !== 'undefined') speechSynthesis.cancel()
  }
  pause() { if (typeof speechSynthesis !== 'undefined') speechSynthesis.pause() }
  resume() { if (typeof speechSynthesis !== 'undefined') speechSynthesis.resume() }

  // A rep count: queued behind whatever is being said (never cutting it off, never dropped by a cancel).
  count(text: string) {
    this.onCaption(text)
    if (this.muted || typeof speechSynthesis === 'undefined') return
    const u = new SpeechSynthesisUtterance(text)
    u.voice = this.voice ?? pickVoice(); u.volume = this.volume; u.rate = 1
    speechSynthesis.speak(u)
  }

  say(lines: string[], onDone: () => void) {
    const busy = typeof speechSynthesis !== 'undefined' && (speechSynthesis.speaking || speechSynthesis.pending)
    this.cancel()
    const gen = this.gen
    const next = (i: number) => {
      if (gen !== this.gen) return
      if (i >= lines.length) return onDone()
      const text = lines[i]
      this.onCaption(text)
      const advance = () => next(i + 1)
      if (this.muted || typeof speechSynthesis === 'undefined') {
        // No audio: keep the pace so captions and timing still work.
        this.fallback = setTimeout(advance, (text.split(/\s+/).length / 2.4) * 1000)
        return
      }
      const u = new SpeechSynthesisUtterance(text)
      u.voice = this.voice ?? pickVoice(); u.volume = this.volume; u.rate = 0.95
      u.onend = advance
      u.onerror = advance // an engine error must not freeze the session
      speechSynthesis.speak(u)
    }
    // Chrome can drop an utterance spoken in the same instant as a cancel(); wait a moment after interrupting.
    if (busy) setTimeout(() => next(0), 70)
    else next(0)
  }
}
