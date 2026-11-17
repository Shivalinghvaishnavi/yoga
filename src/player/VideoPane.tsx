import { useCallback, useState } from 'react'
import { exercises } from '../data/exercises.ts'
import { videos, type VideoEntry } from '../data/videos.ts'
import { YtPlayer } from './YtPlayer.tsx'

export function embedSrc(v: VideoEntry): string {
  const loop = v.loopable ? `&loop=1&playlist=${v.youtubeId}` : ''
  return `https://www.youtube-nocookie.com/embed/${v.youtubeId}?autoplay=1&mute=1&controls=0&rel=0&modestbranding=1&playsinline=1&cc_load_policy=0&disablekb=1&fs=0&iv_load_policy=3&start=${v.start}${v.end > 0 ? `&end=${v.end}` : ''}${loop}`
}

// Muted, controls hidden: our own voice leads. `replayKey` forces a fresh load for Replay.
export function VideoPane({ exerciseId, replayKey, paused }: { exerciseId: string; replayKey: number; paused: boolean }) {
  const [failure, setFailure] = useState<{ id: string; why: string } | null>(null)
  const onFail = useCallback((why: string) => setFailure({ id: exerciseId, why }), [exerciseId])
  const ex = exercises[exerciseId]
  const v = ex.videoId ? videos[ex.videoId] : undefined
  if (exerciseId === 'breath_relax' || exerciseId === 'gentle_breath') {
    return (
      <div className="video pacer" role="img" aria-label="Breathing guide: in for four, out for six">
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
