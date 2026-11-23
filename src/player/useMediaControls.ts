import { useEffect, useRef } from 'react'

// Bluetooth headset / keyboard media keys control the session through the browser's Media Session.
// Browsers only route those keys to a page that is playing audio, so a silent looping sound is played while a session runs.
let silentUrl = ''
function silentWav(): string {
  if (silentUrl) return silentUrl
  const rate = 8000, n = rate, bytes = new Uint8Array(44 + n * 2), v = new DataView(bytes.buffer)
  const str = (o: number, s: string) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)) }
  str(0, 'RIFF'); v.setUint32(4, 36 + n * 2, true); str(8, 'WAVE'); str(12, 'fmt '); v.setUint32(16, 16, true)
  v.setUint16(20, 1, true); v.setUint16(22, 1, true); v.setUint32(24, rate, true); v.setUint32(28, rate * 2, true)
  v.setUint16(32, 2, true); v.setUint16(34, 16, true); str(36, 'data'); v.setUint32(40, n * 2, true)
  silentUrl = URL.createObjectURL(new Blob([bytes], { type: 'audio/wav' }))
  return silentUrl
}

interface Controls { title: string; subtitle: string; paused: boolean; onPause: () => void; onResume: () => void; onNext: () => void; onPrevious: () => void }

export function useMediaControls(c: Controls) {
  const audio = useRef<HTMLAudioElement | null>(null)
  const latest = useRef(c)
  latest.current = c

  useEffect(() => {
    const ms = 'mediaSession' in navigator ? navigator.mediaSession : null
    const a = new Audio(silentWav())
    a.loop = true
    audio.current = a
    const set = (name: MediaSessionAction, fn: () => void) => { try { ms?.setActionHandler(name, fn) } catch { /* action not supported here */ } }
    set('play', () => latest.current.onResume())
    set('pause', () => latest.current.onPause())
    set('nexttrack', () => latest.current.onNext())
    set('previoustrack', () => latest.current.onPrevious())
    if (import.meta.env.DEV) (window as unknown as Record<string, unknown>).__media = { play: () => latest.current.onResume(), pause: () => latest.current.onPause(), next: () => latest.current.onNext(), previous: () => latest.current.onPrevious() }
    return () => {
      a.pause(); a.removeAttribute('src'); audio.current = null
      for (const n of ['play', 'pause', 'nexttrack', 'previoustrack'] as MediaSessionAction[]) set(n, null as unknown as () => void)
      if (ms) { ms.metadata = null; ms.playbackState = 'none' }
    }
  }, [])

  useEffect(() => {
    const ms = 'mediaSession' in navigator ? navigator.mediaSession : null
    if (ms) {
      ms.metadata = new MediaMetadata({ title: c.title, artist: c.subtitle, album: 'Guided workout' })
      ms.playbackState = c.paused ? 'paused' : 'playing'
    }
    const a = audio.current
    if (a) { if (c.paused) a.pause(); else a.play().catch(() => {}) }
  }, [c.title, c.subtitle, c.paused])
}
