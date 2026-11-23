import { schedule } from '../src/data/schedule.ts'
import { exercises } from '../src/data/exercises.ts'
import { compileDay } from '../src/engine/compile.ts'
import { buildCues } from '../src/engine/cues.ts'

// Shows the first spoken cues for a breathing step and the end of a timed hold, and checks nothing is late or too crowded.
const day = (d: number, id: string) => compileDay(schedule[d], 1).find((s) => s.kind === 'work' && s.exerciseId === id)!
const show = (d: number, id: string, from: number, to: number) => {
  const st = day(d, id), c = buildCues(st, exercises[id])
  console.log(`${id} (${st.durationSec}s): ${c.length} cues`)
  for (const x of c.filter((x) => x.at >= from && x.at <= to)) console.log(`   ${x.at.toFixed(1).padStart(6)}s  ${x.text}`)
}
show(0, 'breath_relax', 0, 22); show(1, 'gentle_breath', 0, 12); show(6, 'body_scan', 0, 12); show(1, 'childs_pose', 160, 181); show(5, 'butterfly', 110, 125)
for (const d of schedule) for (const s of compileDay(d, 12)) {
  if (s.kind !== 'work') continue
  const c = buildCues(s, exercises[s.exerciseId])
  if (c.some((x) => x.at > s.durationSec)) throw new Error('late cue ' + s.exerciseId)
  for (let i = 1; i < c.length; i++) if (s.mode === 'timed' && c[i].at - c[i - 1].at < 0.9) throw new Error('crowded cues ' + s.exerciseId + ' ' + c[i].at)
}
console.log('ok')
