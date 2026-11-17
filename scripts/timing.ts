import { schedule } from '../src/data/schedule.ts'
import { compileDay, totalSec } from '../src/engine/compile.ts'

// Prints total minutes per day for each week (spoken briefings included).
const weeks = process.argv[2] ? [Number(process.argv[2])] : [1, 3, 5, 7, 9, 11]
console.log('week  ' + schedule.map((d) => 'D' + d.day).join('    '))
for (const w of weeks) {
  const row = schedule.map((d) => (totalSec(compileDay(d, w)) / 60).toFixed(1).padStart(4))
  console.log(String(w).padStart(4) + '  ' + row.join('  '))
}
