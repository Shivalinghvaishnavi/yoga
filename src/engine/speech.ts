const PREFERRED = ['Samantha', 'Karen', 'Tara', 'Flo', 'Shelley', 'Sandy', 'Google UK English Female']

export function pickVoice(): SpeechSynthesisVoice | null {
  if (typeof speechSynthesis === 'undefined') return null
  const en = speechSynthesis.getVoices().filter((v) => v.lang.toLowerCase().startsWith('en'))
  for (const name of PREFERRED) {
    const hit = en.find((v) => v.name.startsWith(name))
    if (hit) return hit
  }
  return en[0] ?? null
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

  say(lines: string[], onDone: () => void) {
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
    next(0)
  }
}
