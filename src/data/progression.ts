// 12-week progression. Rule: each two-week block changes ONE thing (sets, reps, resistance or tempo).
export interface WeekParams {
  week: number
  phase: 1 | 2 | 3
  phaseName: string
  extraSet: boolean      // one more set on the key lifts
  repsAdd: number        // added to every rep target
  resistance: 'light' | 'medium'
  tempoSec: number       // seconds per rep
  walkAdd: number        // seconds added to walking on walk-focused days
  changes: string        // what is new compared with the previous block
}

// Key lifts that get a third set. Other exercises keep their set count so sessions stay near 45 minutes.
export const KEY_LIFTS = new Set(['band_squat', 'band_rdl', 'band_deadlift', 'glute_bridge'])
// Walk-focused days (Tue, Thu, Sat) lengthen their walking; strength days (Mon, Wed, Fri) keep walking steady.
export const WALK_DAYS = new Set([1, 3, 5])

export const phases = [
  { name: 'Foundation', weeks: '1-4', goal: 'Learn the movements, keep effort comfortable. Two sets, light tube tension.' },
  { name: 'Strength development', weeks: '5-8', goal: 'Build strength with a third set on the key lifts, then a few more reps. Walking days get longer.' },
  { name: 'Endurance and strength', weeks: '9-12', goal: 'Step up the tube tension, then slow each rep down for control. Walking days get longer again.' },
]

const blocks: Array<Omit<WeekParams, 'week' | 'phase' | 'phaseName'>> = [
  { extraSet: false, repsAdd: 0, resistance: 'light', tempoSec: 4, walkAdd: 0, changes: 'Weeks 1-2: learn the movements. Base reps, two sets, light tension.' },
  { extraSet: false, repsAdd: 2, resistance: 'light', tempoSec: 4, walkAdd: 0, changes: 'Weeks 3-4: two more reps per set. Nothing else changes.' },
  { extraSet: true, repsAdd: 2, resistance: 'light', tempoSec: 4, walkAdd: 60, changes: 'Weeks 5-6: a third set on the key lifts. Same reps, same tension. Walking days gain a minute.' },
  { extraSet: true, repsAdd: 4, resistance: 'light', tempoSec: 4, walkAdd: 120, changes: 'Weeks 7-8: two more reps per set. Walking days gain another minute.' },
  { extraSet: true, repsAdd: 4, resistance: 'medium', tempoSec: 4, walkAdd: 120, changes: 'Weeks 9-10: tube tension goes up one level. Same reps and sets.' },
  { extraSet: true, repsAdd: 2, resistance: 'medium', tempoSec: 5, walkAdd: 180, changes: 'Weeks 11-12: slower, more controlled reps (five seconds each), with two fewer reps so the set takes about as long. Walking days gain another minute.' },
]

export function paramsFor(week: number): WeekParams {
  const w = Math.min(12, Math.max(1, Math.round(week)))
  const block = blocks[Math.floor((w - 1) / 2)]
  const phase = w <= 4 ? 1 : w <= 8 ? 2 : 3
  return { week: w, phase, phaseName: phases[phase - 1].name, ...block }
}
