import { videos } from '../src/data/videos.ts'
for (const [k, v] of Object.entries(videos)) console.log(`${k}\t${v.youtubeId}\t${v.start}\t${v.end}\t${v.creator}`)
