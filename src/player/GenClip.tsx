import { useEffect, useRef } from 'react'
import type { Step } from '../data/types.ts'
import type { ClipInfo } from '../data/clipManifest.ts'
import { COUNT_AT } from '../engine/cues.ts'

export function clipFile(clip: ClipInfo, side?: 'left' | 'right'): string {
  return (side === 'right' ? clip.right : clip.left) ?? clip.file ?? clip.left ?? clip.right ?? ''
}

// Plays a generated instructor loop. Rep loops are slowed or sped so that one rep = one spoken count,
// and each set starts on the starting pose and begins moving exactly when the first count is spoken.
export function GenClip({ clip, step, token, paused, onFail }: { clip: ClipInfo; step: Step; token: number; paused: boolean; onFail: (why: string) => void }) {
  const ref = useRef<HTMLVideoElement>(null)
  const want = useRef(true)
  const pausedRef = useRef(paused)
  const file = clipFile(clip, step.side ?? 'left')
  const repLoop = step.mode === 'reps' && clip.repsPerLoop > 0
  const rate = repLoop ? Math.min(4, Math.max(0.25, clip.period / clip.repsPerLoop / step.tempo)) : 1

  useEffect(() => {
    const v = ref.current
    if (!v) return
    let timer: ReturnType<typeof setTimeout> | undefined
    v.playbackRate = rate
    if (step.kind === 'rest' || (step.kind === 'work' && repLoop)) {
      v.pause(); v.currentTime = 0; want.current = false          // hold the starting pose
      if (step.kind === 'work') timer = setTimeout(() => { want.current = true; if (!pausedRef.current) v.play().catch(() => {}) }, COUNT_AT * 1000)
    } else {
      want.current = true
      if (!pausedRef.current) v.play().catch(() => {})
    }
    return () => clearTimeout(timer)
  }, [token, rate, file, step.kind, repLoop])

  useEffect(() => {
    pausedRef.current = paused
    const v = ref.current
    if (!v) return
    if (paused) v.pause()
    else if (want.current) v.play().catch(() => {})
  }, [paused])

  return <video ref={ref} key={file} className="video gen" src={`${import.meta.env.BASE_URL}clips/${file}`} muted loop playsInline preload="auto"
    onError={() => onFail('The animation could not be loaded.')} />
}
