import { schedule } from '../src/data/schedule.ts'
import { exercises } from '../src/data/exercises.ts'
import { videos } from '../src/data/videos.ts'

const used = new Set(schedule.flatMap((d) => d.items.map((i) => i.exerciseId)))
const missing = [...used].filter((id) => !exercises[id])
const noVideo = [...used].filter((id) => exercises[id] && !videos[exercises[id].videoId ?? ''])
console.log('exercises used:', used.size, '| undefined:', missing, '| without video:', noVideo)
for (const [k, v] of Object.entries(videos)) if (!exercises[k]) console.log('orphan video entry:', k)
