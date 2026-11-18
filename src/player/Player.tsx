import { useEffect, useRef, useState } from 'react'
import { exercises } from '../data/exercises.ts'
import { schedule } from '../data/schedule.ts'
import { totalSec } from '../engine/compile.ts'
import { COUNT_AT } from '../engine/cues.ts'
import { VideoPane, type VideoSource } from './VideoPane.tsx'
import { usePlayer } from './usePlayer.ts'

const mmss = (s: number) => {
  const t = Math.max(0, Math.ceil(s))
  return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}`
}

export function Player({ day, week, resumeFrom, source, onExit }: { day: number; week: number; resumeFrom: number; source: VideoSource; onExit: () => void }) {
  const { runner, speaker, snap, caption, steps } = usePlayer(day, week, resumeFrom)
  const [volume, setVolume] = useState(1)
  const [muted, setMuted] = useState(false)
  const [captions, setCaptions] = useState(true)
  const [replayKey, setReplayKey] = useState(0)
  const root = useRef<HTMLDivElement>(null)

  useEffect(() => { speaker.volume = volume }, [speaker, volume])
  useEffect(() => { speaker.setMuted(muted) }, [speaker, muted])
  useEffect(() => {
    if (snap.status === 'paused') speaker.pause()
    else if (snap.status === 'running') speaker.resume()
  }, [speaker, snap.status])
  useEffect(() => {
    // Not guarded by a ref: StrictMode runs cleanup (which stops the clock) then this again.
    runner.speed = Number(new URLSearchParams(location.search).get('speed')) || 1
    runner.start(resumeFrom)
    let lock: WakeLockSentinel | null = null
    navigator.wakeLock?.request('screen').then((l) => { lock = l }).catch(() => {})
    return () => { lock?.release().catch(() => {}) }
  }, [runner, resumeFrom])

  const step = snap.step
  const ex = step ? exercises[step.exerciseId] : null
  const planned = totalSec(steps)
  const done = steps.slice(0, snap.index).reduce((a, s) => a + s.durationSec, 0) + snap.elapsed
  const remaining = step ? step.durationSec - snap.elapsed : 0
  const rep = step?.kind === 'work' && step.mode === 'reps' ? Math.min(step.target, snap.elapsed < COUNT_AT ? 1 : Math.floor((snap.elapsed - COUNT_AT) / step.tempo) + 1) : 0
  const nextEx = steps.slice(snap.index + 1).find((s) => s.exerciseId !== step?.exerciseId)
  const paused = snap.status === 'paused'
  const toggle = () => (paused ? runner.resume() : runner.pause())
  const replay = () => { runner.replay(); setReplayKey((k) => k + 1) }
  const fullscreen = () => (document.fullscreenElement ? document.exitFullscreen() : root.current?.requestFullscreen())

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.code === 'Space') { e.preventDefault(); toggle() }
      else if (e.key === 'ArrowRight') runner.skip()
      else if (e.key === 'r') replay()
      else if (e.key === 'm') setMuted((m) => !m)
      else if (e.key === 'c') setCaptions((c) => !c)
      else if (e.key === 'f') fullscreen()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  })

  if (snap.status === 'done') {
    const mins = Math.round(planned / 60)
    return (
      <div className="player done">
        <h1>Session complete</h1>
        <p>{schedule[day].title}: about {mins} minutes, {new Set(steps.map((s) => s.exerciseId)).size} exercises.</p>
        <p>Well done. Drink some water and rest.</p>
        <button onClick={() => { runner.restart() }}>Do it again</button> <button onClick={onExit}>Back to days</button>
      </div>
    )
  }

  return (
    <div className="player" ref={root}>
      <div className="bar"><div style={{ width: `${Math.min(100, (done / planned) * 100)}%` }} /></div>
      <div className="hud">
        <div className="hud-main">
          <div className="title">{step?.kind === 'rest' ? 'Rest' : ex?.name}{step?.side ? ` · ${step.side} side` : ''}</div>
          <div className="meta">
            {step?.kind === 'work' && <span>Set {step.set} of {step.totalSets}</span>}
            {step?.kind === 'brief' && <span>Get ready</span>}
            {rep > 0 && <span>Rep {rep} of {step?.target}</span>}
            {nextEx && <span className="next">Next: {exercises[nextEx.exerciseId].name}</span>}
          </div>
        </div>
        {step?.kind !== 'brief' && <div className="timer">{mmss(remaining)}</div>}
      </div>
      <div className="stage">
        {step && ex && <VideoPane step={step} replayKey={replayKey} paused={paused} token={snap.token} source={source} />}
        {paused && <div className="paused">Paused</div>}
      </div>
      {captions && <div className="caption">{caption}</div>}
      <div className="controls">
        <button onClick={toggle}>{paused ? 'Resume' : 'Pause'}</button>
        <button onClick={() => runner.skip()}>Skip</button>
        <button onClick={replay}>Replay</button>
        <button onClick={() => runner.restart()}>Restart</button>
        <button onClick={() => setMuted(!muted)}>{muted ? 'Unmute' : 'Mute'}</button>
        <input type="range" min="0" max="1" step="0.1" value={volume} onChange={(e) => setVolume(+e.target.value)} aria-label="Volume" />
        <button onClick={() => setCaptions(!captions)}>Captions {captions ? 'on' : 'off'}</button>
        <button onClick={fullscreen}>Full screen</button>
        <button onClick={() => { runner.stop(); speaker.cancel(); onExit() }}>Exit</button>
      </div>
    </div>
  )
}
