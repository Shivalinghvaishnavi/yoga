import type { Step } from '../data/types.ts'
import type { ClipInfo } from '../data/clipManifest.ts'
import { clipManifest } from '../data/clipManifest.ts'
import { BREATH_IDS, COUNT_AT } from './cues.ts'

// How a work step is counted aloud. Every exercise is counted: reps at the rep tempo; movement loops (hip circles, marching,
// walking...) one number per loop of the animation, wrapping 1-8 or 1-10; holds one number per second, wrapping 1-10.
// The last 11 seconds belong to the spoken time countdown (see cues.ts).
export interface CountPlan { every: number; wrap: number; last: number; kind: 'reps' | 'loop' | 'seconds' }

export function countPlan(step: Step, clip: ClipInfo | undefined = clipManifest[step.exerciseId]): CountPlan | null {
  if (step.kind !== 'work') return null
  if (step.mode === 'reps') return { every: step.tempo, wrap: 0, last: step.target, kind: 'reps' }
  if (step.durationSec < 20 || BREATH_IDS.has(step.exerciseId)) return null   // breathing is guided by inhale / exhale counts instead
  if (clip && clip.repsPerLoop > 0) {
    const every = clip.period / clip.repsPerLoop
    return { every, wrap: every <= 3 ? 8 : 10, last: Math.max(1, Math.floor((step.durationSec - 11 - COUNT_AT) / every) + 1), kind: 'loop' }
  }
  return { every: 1, wrap: 10, last: Math.max(1, Math.floor(step.durationSec - 11 - COUNT_AT) + 1), kind: 'seconds' }
}

export function countAt(plan: CountPlan, elapsed: number): number {
  return elapsed < COUNT_AT ? 0 : Math.floor((elapsed - COUNT_AT) / plan.every) + 1
}

export const shown = (plan: CountPlan, n: number) => (plan.wrap ? ((n - 1) % plan.wrap) + 1 : n)
