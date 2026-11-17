import { exercises } from '../src/data/exercises.ts'
import { briefText } from '../src/engine/compile.ts'
console.log(briefText(exercises.band_squat, 'medium').slice(0, 3))
console.log(briefText(exercises.bw_squat, undefined).slice(0, 2))
