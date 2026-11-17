import { schedule } from '../src/data/schedule.ts'
import { compileDay, totalSec } from '../src/engine/compile.ts'
import { Runner } from '../src/engine/runner.ts'

const steps = compileDay(schedule[0])
const r = new Runner(steps)
const seen: number[] = []
let tokens = 0, lastToken = -1
r.subscribe((s) => { if (s.token !== lastToken) { lastToken = s.token; tokens++; if (s.step) seen.push(s.index) } })
r.start(); r.stop() // use manual ticks, not the real interval

// pause must freeze time
r.pause(); const e0 = r.elapsed; r.tick(5); console.assert(r.elapsed === e0, 'paused clock moved'); r.resume()

let simulated = 0
while (r.status !== 'done') {
  if (r.step?.kind === 'brief' && r.elapsed >= 3) r.markSpeechDone()
  r.tick(0.25); simulated += 0.25
  if (simulated > 7200) throw new Error('did not finish')
}
console.assert(seen.length === steps.length, `visited ${seen.length}/${steps.length}`)
console.assert(seen.every((v, i) => v === i), 'steps out of order')
console.log(`ok: ${steps.length} steps in order, simulated ${(simulated / 60).toFixed(1)} min (planned ${(totalSec(steps) / 60).toFixed(1)}), tokens ${tokens}`)

// skip + replay
const r2 = new Runner(steps); r2.start(); r2.stop()
const t1 = r2.token; r2.skip(); console.assert(r2.index === 1 && r2.token > t1, 'skip')
const t2 = r2.token; r2.replay(); console.assert(r2.index === 1 && r2.token > t2 && r2.elapsed === 0, 'replay')
console.log('ok: skip and replay')
