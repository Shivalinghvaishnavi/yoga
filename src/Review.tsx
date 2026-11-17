import { useCallback, useState } from 'react'
import { exercises } from './data/exercises.ts'
import { videos } from './data/videos.ts'
import { YtPlayer } from './player/YtPlayer.tsx'

// Maintenance page (open with ?review): plays every logged clip through the same player the app uses,
// so each one can be checked by eye. The status line says whether the clip started or failed.
const keys = Object.keys(videos)

function Grid({ from, count }: { from: number; count: number }) {
  const noop = useCallback(() => {}, [])
  return (
    <div className="rv-grid">
      {keys.slice(from, from + count).map((key, n) => (
        <div key={key} className="rv-cell">
          <div className="rv-meta">{from + n + 1}. {exercises[key]?.name ?? key} | {videos[key].creator}</div>
          <div className="rv-frame"><YtPlayer video={videos[key]} paused={false} onFail={noop} /></div>
        </div>
      ))}
    </div>
  )
}

export default function Review() {
  const q = new URLSearchParams(location.search)
  if (q.get('from')) return <Grid from={Number(q.get('from')) - 1} count={Number(q.get('count') ?? 6)} />
  return <Single />
}

function Single() {
  const [i, setI] = useState(0)
  const [fail, setFail] = useState<{ key: string; why: string } | null>(null)
  const k = keys[i], v = videos[k]
  const onFail = useCallback((why: string) => setFail({ key: k, why }), [k])
  const failed = fail?.key === k
  return (
    <div className="review">
      <div className="rv-head">
        <button onClick={() => setI((n) => (n + keys.length - 1) % keys.length)}>Prev</button>
        <strong>{i + 1}/{keys.length} {exercises[k]?.name ?? k}</strong>
        <button onClick={() => setI((n) => (n + 1) % keys.length)}>Next</button>
      </div>
      <div className="rv-meta">{v.creator} | {v.title} | {v.youtubeId} | {v.start}-{v.end || 'end'}s</div>
      <div className="rv-status" data-key={k} data-failed={failed ? fail?.why : ''}>{failed ? `FAILED: ${fail?.why}` : 'loading or playing'}</div>
      <div className="rv-frame"><YtPlayer key={k} video={v} paused={false} onFail={onFail} /></div>
    </div>
  )
}
