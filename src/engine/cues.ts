import type { Exercise, Step } from '../data/types.ts'

// Rep k is counted at (k-1)*tempo + COUNT_AT seconds. The offset leaves room for the "Set 1 of 2. Begin." line first.
export const COUNT_AT = 2.5

export interface Cue { at: number; text: string } // `at` = seconds into the step

const WALK = [
  'Keep a steady pace.', 'Shoulders relaxed, stand tall.', 'Breathe easily. You should be able to talk.',
  'You are doing really well. Keep it going.',
]

// Breathing steps are guided continuously: one 10 s cycle = 4 s in, 6 s out, matching the on-screen breathing circle.
export const BREATH_IDS = new Set(['gentle_breath', 'breath_relax', 'diaphragm_breath', 'body_scan'])

function breathCues(d: number): Cue[] {
  const cues: Cue[] = []
  for (let base = 0.5; base < d - 14; base += 10) {
    cues.push({ at: base, text: 'Inhale, two, three, four.' }, { at: base + 4.0, text: 'Exhale, two, three, four, five, six.' })
  }
  return cues
}

const lower = (s: string) => s.charAt(0).toLowerCase() + s.slice(1)
const WORDS = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']

// Time remaining, spoken for every timed step: minutes left on long ones, 30 and 20 seconds, then ten down to one.
function timeCallouts(d: number): Cue[] {
  const out: Cue[] = []
  if (d >= 630) out.push({ at: d - 300, text: 'Five minutes left.' })
  if (d >= 360) out.push({ at: d - 180, text: 'Three minutes left.' })
  if (d >= 150) out.push({ at: d - 60, text: 'One minute left.' })
  if (d >= 70) out.push({ at: d - 30, text: 'Thirty seconds left.' })
  if (d >= 45) out.push({ at: d - 20, text: 'Twenty seconds.' })
  if (d >= 20) for (let i = 10; i >= 1; i--) out.push({ at: d - i, text: WORDS[i - 1] })
  return out
}

// Spoken cues scheduled inside a work step. Rep and loop counts are spoken separately (see counting.ts).
export function buildCues(step: Step, ex: Exercise): Cue[] {
  if (step.kind !== 'work') return []
  const posture = ex.posture[0] ? `${ex.posture[0]}.` : ''
  if (step.mode === 'reps') {
    // Cues start 1.2 s after a count so the next count does not cut them off.
    const t = step.tempo, after = (k: number) => (k - 1) * t + COUNT_AT + 1.2, cues: Cue[] = []
    if (step.target >= 6) cues.push({ at: after(2), text: 'Slow and controlled. No rushing.' })
    if (step.target >= 8) cues.push({ at: after(Math.floor(step.target / 2)), text: `Halfway. ${posture}` })
    if (step.target >= 10 && ex.mistakes[0]) cues.push({ at: after(step.target - 3), text: `Avoid ${lower(ex.mistakes[0])}.` })
    return cues
  }
  const d = step.durationSec
  if (BREATH_IDS.has(ex.id)) {
    const cues = breathCues(d)
    if (d >= 120) cues.push({ at: d / 2 - 1.5, text: 'Halfway there.' })
    if (d >= 40) cues.push({ at: d - 10, text: 'Begin to bring your awareness back.' })
    return cues.sort((a, b) => a.at - b.at)
  }
  const calls = timeCallouts(d)
  const clear = (at: number) => calls.every((c) => Math.abs(c.at - at) > 4)   // time callouts win over other cues
  const cues: Cue[] = []
  if (step.section === 'cardio') {
    for (let at = 60, i = 0; at < d - 30; at += 60, i++) if (clear(at)) cues.push({ at, text: WALK[i % WALK.length] })
  } else if (d >= 30) {
    if (clear(d / 2)) cues.push({ at: d / 2, text: `Halfway there. ${posture}` })
    for (let at = 60; at < d - 15; at += 60) if (Math.abs(at - d / 2) > 15 && clear(at)) cues.push({ at, text: ex.breathing })
  }
  return [...cues, ...calls].sort((a, b) => a.at - b.at)
}

export function restLine(step: Step, next: Step | undefined, nextName: string): string {
  const doneWord = next && next.exerciseId !== step.exerciseId ? 'Exercise complete.' : 'Set complete.'
  return `${doneWord} Rest. Next up, ${nextName}.`
}
