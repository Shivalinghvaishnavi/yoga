import type { Exercise, Step } from '../data/types.ts'

// Rep k is counted at (k-1)*tempo + COUNT_AT seconds. The offset leaves room for the "Set 1 of 2. Begin." line first.
export const COUNT_AT = 2.5

export interface Cue { at: number; text: string } // `at` = seconds into the step

const RELAX = [
  'Breathe in slowly through your nose.', 'Let your shoulders sink and your jaw soften.',
  'Breathe out slowly, a little longer than the breath in.', 'Let the floor hold your weight.',
  'Nothing to do now. Just rest.',
]
const WALK = [
  'Keep a steady pace.', 'Shoulders relaxed, stand tall.', 'Breathe easily. You should be able to talk.',
  'You are doing really well. Keep it going.',
]
const lower = (s: string) => s.charAt(0).toLowerCase() + s.slice(1)

// Spoken cues scheduled inside a work step. Rep counts are spoken separately, one per rep.
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
  const d = step.durationSec, cues: Cue[] = []
  const pool = step.section === 'relax' ? RELAX : step.section === 'cardio' ? WALK : null
  if (pool) {
    const gap = step.section === 'relax' ? 50 : 60
    for (let at = gap, i = 0; at < d - 20; at += gap, i++) cues.push({ at, text: pool[i % pool.length] })
    if (d >= 120) {
      const near = cues.find((c) => Math.abs(c.at - d / 2) < 15)
      if (near) near.text = `Halfway there. ${near.text}`
      else cues.push({ at: d / 2, text: 'Halfway there.' })
    }
  } else if (d >= 30) {
    cues.push({ at: d / 2, text: `Halfway there. ${posture}` })
    for (let at = 60; at < d - 15; at += 60) if (Math.abs(at - d / 2) > 15) cues.push({ at, text: ex.breathing })
  }
  if (d >= 40) cues.push({ at: d - 10, text: step.section === 'relax' ? 'Begin to bring your awareness back.' : 'Last ten seconds.' })
  return cues.sort((a, b) => a.at - b.at)
}

export function restLine(step: Step, next: Step | undefined, nextName: string): string {
  const doneWord = next && next.exerciseId !== step.exerciseId ? 'Exercise complete.' : 'Set complete.'
  return `${doneWord} Rest. Next up, ${nextName}.`
}
