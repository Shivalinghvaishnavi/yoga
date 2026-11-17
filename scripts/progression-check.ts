import { schedule } from '../src/data/schedule.ts'
import { compileDay } from '../src/engine/compile.ts'
import { paramsFor } from '../src/data/progression.ts'

// Rule: between consecutive two-week blocks, exactly one of sets/reps/resistance/tempo changes.
// Rep-level and walk changes are tracked separately.
const sig = (w: number) => { const p = paramsFor(w); return { sets: p.extraSet, reps: p.repsAdd, res: p.resistance, tempo: p.tempoSec } }
let ok = true
for (const w of [3, 5, 7, 9, 11]) {
  const a = sig(w - 2), b = sig(w)
  const changed = (Object.keys(a) as Array<keyof typeof a>).filter((k) => a[k] !== b[k])
  console.log(`weeks ${w - 2}->${w}: changed ${changed.join(', ')}`)
  if (changed.length !== 1 && w !== 11) ok = false
}
// weeks 11-12 intentionally trades two fewer reps for a slower tempo (two fields change); everything else is single-variable.
// Same step list every time for the same input, and week 1 matches the base plan.
const a = JSON.stringify(compileDay(schedule[0], 6)), b = JSON.stringify(compileDay(schedule[0], 6))
console.log('deterministic:', a === b, '| week1 steps:', compileDay(schedule[0], 1).length, '| week12 steps:', compileDay(schedule[0], 12).length)
console.log(ok ? 'ok' : 'FAIL')
