import { schedule } from '../src/data/schedule.ts'
import { exercises } from '../src/data/exercises.ts'
import { compileDay } from '../src/engine/compile.ts'
import { buildCues } from '../src/engine/cues.ts'

// Prints the tail of timed steps (time countdown) and checks no cue is late or crowded.
const find = (d: number, id: string) => compileDay(schedule[d], 1).find((s) => s.kind === 'work' && s.exerciseId === id)!
const tail = (d: number, id: string, from: number) => {
  const st = find(d, id), c = buildCues(st, exercises[id])
  console.log(`${id} (${st.durationSec}s): ${c.length} cues; from ${from}s:`, c.filter((x) => x.at >= from).map((x) => `${x.at.toFixed(0)}:${x.text}`).join(' | '))
}
tail(0, 'hip_circles', 60); tail(0, 'brisk_walk', 500); tail(1, 'doorway_chest', 40); tail(0, 'march', 130)
for (const d of schedule) for (const s of compileDay(d, 12)) {
  if (s.kind !== 'work') continue
  const c = buildCues(s, exercises[s.exerciseId])
  if (c.some((x) => x.at > s.durationSec)) throw new Error('late cue ' + s.exerciseId)
  for (let i = 1; i < c.length; i++) if (s.mode === 'timed' && c[i].at - c[i - 1].at < 0.9) throw new Error('crowded cues ' + s.exerciseId + ' ' + c[i].at)
}
console.log('ok')
