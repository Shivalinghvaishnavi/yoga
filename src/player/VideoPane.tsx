import { useCallback, useState } from 'react'
import { exercises } from '../data/exercises.ts'
import { videos, type VideoEntry } from '../data/videos.ts'
import { YtPlayer } from './YtPlayer.tsx'
import { GenClip } from './GenClip.tsx'
import { clipManifest } from '../data/clipManifest.ts'
import type { Step } from '../data/types.ts'

export function embedSrc(v: VideoEntry): string {
  const loop = v.loopable ? `&loop=1&playlist=${v.youtubeId}` : ''
  return `https://www.youtube-nocookie.com/embed/${v.youtubeId}?autoplay=1&mute=1&controls=0&rel=0&modestbranding=1&playsinline=1&cc_load_policy=0&disablekb=1&fs=0&iv_load_policy=3&start=${v.start}${v.end > 0 ? `&end=${v.end}` : ''}${loop}`
}

// Muted, controls hidden: our own voice leads. `replayKey` forces a fresh load for Replay.
export type VideoSource = 'animated' | 'real'

export function VideoPane({ step, replayKey, paused, token, source }: { step: Step; replayKey: number; paused: boolean; token: number; source: VideoSource }) {
  const exerciseId = step.exerciseId
  const [genFailed, setGenFailed] = useState<string | null>(null)
  const onGenFail = useCallback(() => setGenFailed(exerciseId), [exerciseId])
  const [failure, setFailure] = useState<{ id: string; why: string } | null>(null)
  const onFail = useCallback((why: string) => setFailure({ id: exerciseId, why }), [exerciseId])
  const ex = exercises[exerciseId]
  const v = ex.videoId ? videos[ex.videoId] : undefined
  const clip = clipManifest[exerciseId]
  const breathing = exerciseId === 'breath_relax' || exerciseId === 'gentle_breath'
  if (!breathing && source === 'animated' && clip && genFailed !== exerciseId) {
    return <GenClip key={`${exerciseId}-${replayKey}`} clip={clip} step={step} token={token} paused={paused} onFail={onGenFail} />
  }
  if (breathing) {
    return (
      <div key={`pacer-${token}`} className="video pacer" role="img" aria-label="Breathing guide: in for four, out for six">
        <div className="orb" />
      </div>
    )
  }
  if (!v || failure?.id === exerciseId) {
    return (
      <div className="video fallback" role="img" aria-label={`Demonstration unavailable for ${ex.name}`}>
        <p className="fb-title">Demonstration video not available{failure?.id === exerciseId ? ` (${failure.why})` : ''}</p>
        <p className="fb-name">{ex.name}</p>
        <ul>{ex.how.map((t) => <li key={t}>{t}</li>)}</ul>
      </div>
    )
  }
  return (
    <>
      <YtPlayer key={`${exerciseId}-${replayKey}`} video={v} paused={paused} onFail={onFail} />
      <div className="credit">Video: {v.creator} on YouTube</div>
    </>
  )
}
