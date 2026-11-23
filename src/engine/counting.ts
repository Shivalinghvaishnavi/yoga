import type { Step } from '../data/types.ts'
import type { ClipInfo } from '../data/clipManifest.ts'
import { clipManifest } from '../data/clipManifest.ts'
import { COUNT_AT } from './cues.ts'

// How a work step is counted aloud. Rep exercises count reps at the rep tempo. Movement loops (hip circles, marching,
// cat-cow...) count one number per loop of the animation, wrapping 1-8 or 1-10. Holds get a time countdown instead (see cues.ts).
export interface CountPlan { every: number; wrap: number; last: number }

export function countPlan(step: Step, clip: ClipInfo | undefined = clipManifest[step.exerciseId]): CountPlan | null {
  if (step.kind !== 'work') return null
  if (step.mode === 'reps') return { every: step.tempo, wrap: 0, last: step.target }
  if (!clip || clip.repsPerLoop <= 0 || step.section === 'cardio' || step.durationSec < 20) return null
  const every = clip.period / clip.repsPerLoop
  // the spoken time countdown owns the final 11 seconds
  const last = Math.max(1, Math.floor((step.durationSec - 11 - COUNT_AT) / every) + 1)
  return { every, wrap: every <= 3 ? 8 : 10, last }
}

export function countAt(plan: CountPlan, elapsed: number): number {
  return elapsed < COUNT_AT ? 0 : Math.floor((elapsed - COUNT_AT) / plan.every) + 1
}

export const shown = (plan: CountPlan, n: number) => (plan.wrap ? ((n - 1) % plan.wrap) + 1 : n)
