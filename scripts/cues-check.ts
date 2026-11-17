import { schedule } from '../src/data/schedule.ts'
import { exercises } from '../src/data/exercises.ts'
import { compileDay } from '../src/engine/compile.ts'
import { buildCues } from '../src/engine/cues.ts'

// Prints the spoken cues for one example of each kind of step, and checks that no cue lands after the step ends.
const show = (day: number, id: string, week = 1) => {
  const step = compileDay(schedule[day], week).find((s) => s.kind === 'work' && s.exerciseId === id)!
  const cues = buildCues(step, exercises[id])
  console.log(`${id} (${step.mode}, ${step.durationSec}s): ${cues.length} cues`)
  for (const c of cues) console.log(`   ${c.at.toFixed(1).padStart(6)}s  ${c.text}`)
  if (cues.some((c) => c.at > step.durationSec)) throw new Error('cue after end: ' + id)
}
show(0, 'band_squat'); show(0, 'brisk_walk'); show(0, 'breath_relax'); show(1, 'childs_pose'); show(6, 'body_scan')
// every work step in every day: cues inside the step
for (const d of schedule) for (const s of compileDay(d, 12)) if (s.kind === 'work' && buildCues(s, exercises[s.exerciseId]).some((c) => c.at > s.durationSec)) throw new Error('late cue')
console.log('ok')
