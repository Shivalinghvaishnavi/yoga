import { useEffect, useMemo, useRef, useState } from 'react'
import { exercises } from '../data/exercises.ts'
import { schedule } from '../data/schedule.ts'
import { briefText, compileDay } from '../engine/compile.ts'
import { Runner, type Snapshot } from '../engine/runner.ts'
import { COUNT_AT, buildCues, restLine, type Cue } from '../engine/cues.ts'
import { Speaker } from '../engine/speech.ts'
import { clearProgress, saveProgress } from '../engine/storage.ts'

export function usePlayer(day: number, week: number, resumeFrom = 0) {
  const steps = useMemo(() => compileDay(schedule[day], week), [day, week])
  const runner = useMemo(() => new Runner(steps), [steps])
  const speaker = useMemo(() => new Speaker(), [])
  const [snap, setSnap] = useState<Snapshot>(runner.snapshot())
  const [caption, setCaption] = useState('')
  const last = useRef<{ token: number; rep: number; cued: number; cues: Cue[]; next: number }>({ token: -1, rep: 0, cued: 0, cues: [], next: 0 })

  useEffect(() => {
    speaker.onCaption = setCaption
    const off = runner.subscribe((s) => {
      setSnap(s)
      const L = last.current, step = s.step
      if (s.token !== L.token) {
        L.token = s.token; L.rep = 0; L.cued = 0; L.cues = []; L.next = 0
        if (s.status === 'done') { clearProgress(); speaker.say(['Well done. Your session is complete. Take a moment to breathe.'], () => {}); return }
        if (!step) return
        saveProgress({ day, week, index: s.index, savedAt: Date.now() })
        const ex = exercises[step.exerciseId]
        const next = runner.steps[s.index + 1]
        const prev = runner.steps[s.index - 1]
        if (step.kind === 'brief') {
          const praise = prev && prev.kind !== 'brief' ? ['Well done.'] : []
          speaker.say([...praise, ...briefText(ex, step.resistance, week <= 4)], () => runner.markSpeechDone())
        }
        else if (step.kind === 'work') {
          const side = step.side ? `${step.side} side. ` : ''
          speaker.say([`Set ${step.set} of ${step.totalSets}. ${side}Begin.`], () => {})
          L.cues = buildCues(step, ex)
        } else speaker.say([restLine(step, next, exercises[(next ?? step).exerciseId].name)], () => {})
      } else if (step && s.status === 'running') {
        if (step.kind === 'work' && step.mode === 'reps') {
          const rep = s.elapsed < COUNT_AT ? 0 : Math.floor((s.elapsed - COUNT_AT) / step.tempo) + 1
          if (rep > L.rep && rep <= step.target) { L.rep = rep; speaker.count(String(rep)) }
        } else if (step.kind === 'work') { /* timed work: cues below */
        } else if (step.kind === 'rest' && !L.cued && step.durationSec - s.elapsed <= 5) {
          L.cued = 1; speaker.say(['Get ready.'], () => {})
        }
        // Scheduled cues; a cue never fires in the same instant as a rep count.
        if (step.kind === 'work' && L.next < L.cues.length && s.elapsed >= L.cues[L.next].at) {
          speaker.say([L.cues[L.next].text], () => {}); L.next++
        }
      }
    })
    return () => { off(); runner.stop(); speaker.cancel() }
  }, [runner, speaker, day, week])

  return { runner, speaker, snap, caption, steps, resumeFrom }
}
