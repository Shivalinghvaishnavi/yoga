import { useEffect, useRef, useState } from 'react'
import type { VideoEntry } from '../data/videos.ts'

// Minimal typing for the parts of YouTube's IFrame API we use.
interface YTPlayer { destroy(): void; seekTo(s: number, allowSeekAhead: boolean): void; playVideo(): void; pauseVideo(): void; unloadModule?(name: string): void }
interface YTApi { Player: new (el: HTMLElement, opts: unknown) => YTPlayer; PlayerState: { ENDED: number } }
declare global { interface Window { YT?: YTApi; onYouTubeIframeAPIReady?: () => void } }

let apiPromise: Promise<YTApi> | null = null
function loadApi(): Promise<YTApi> {
  if (window.YT?.Player) return Promise.resolve(window.YT)
  apiPromise ??= new Promise((resolve, reject) => {
    const prev = window.onYouTubeIframeAPIReady
    window.onYouTubeIframeAPIReady = () => { prev?.(); resolve(window.YT as YTApi) }
    const s = document.createElement('script')
    s.src = 'https://www.youtube.com/iframe_api'
    s.onerror = () => { apiPromise = null; reject(new Error('YouTube API failed to load')) }
    document.head.appendChild(s)
  })
  return apiPromise
}

// Plays one clip muted, loops it ourselves (YouTube's own loop ignores start/end), and reports failures.
export function YtPlayer({ video, paused, onFail }: { video: VideoEntry; paused: boolean; onFail: (why: string) => void }) {
  const host = useRef<HTMLDivElement>(null)
  const playerRef = useRef<YTPlayer | null>(null)
  const pausedRef = useRef(paused)
  const [ready, setReady] = useState(false)

  // The video follows the session: Pause freezes the instructor, Resume continues.
  useEffect(() => {
    pausedRef.current = paused
    try { if (paused) playerRef.current?.pauseVideo(); else if (ready) playerRef.current?.playVideo() } catch { /* player not ready yet */ }
  }, [paused, ready])

  useEffect(() => {
    let player: YTPlayer | null = null, dead = false
    const stall = setTimeout(() => { if (!dead) onFail('The video is taking too long to load.') }, 30000)
    loadApi().then((YT) => {
      if (dead || !host.current) return
      const el = document.createElement('div')
      host.current.appendChild(el)
      player = playerRef.current = new YT.Player(el, {
        host: 'https://www.youtube-nocookie.com',
        videoId: video.youtubeId,
        playerVars: { autoplay: 1, mute: 1, controls: 0, rel: 0, modestbranding: 1, playsinline: 1, cc_load_policy: 0, disablekb: 1, fs: 0, iv_load_policy: 3, start: video.start, ...(video.end > 0 ? { end: video.end } : {}) },
        events: {
          onStateChange: (e: { data: number }) => {
            if (e.data === 1) { player?.unloadModule?.('captions'); player?.unloadModule?.('cc'); setReady(true); clearTimeout(stall); if (pausedRef.current) player?.pauseVideo() }
            if (e.data === YT.PlayerState.ENDED && video.loopable) { player?.seekTo(video.start, true); player?.playVideo() }
          },
          onError: () => onFail('This video cannot be played here.'),
        },
      })
    }).catch(() => onFail('Could not reach YouTube.'))
    return () => { dead = true; clearTimeout(stall); playerRef.current = null; try { player?.destroy() } catch { /* already gone */ } }
  }, [video, onFail])

  return <div className={`video yt ${ready ? 'on' : ''}`} ref={host} />
}
