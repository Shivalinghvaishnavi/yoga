# Guided Home Fitness Programme

A static web app: pick a day, press Play, and follow a voice-guided 45-minute session with embedded demonstration videos. 12-week progression. No backend, no accounts, no paid services.

## Run

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # static files in dist/
```

Useful URLs while developing:
- `/?speed=20` plays sessions 20x faster (test aid; never use for a real workout).
- `/?review` steps through every logged video clip.

## Where things are

| Concern | File |
|---|---|
| Weekly schedule (exercise order, sets, reps, rests) | `src/data/schedule.ts` |
| Exercise catalogue and spoken instructions | `src/data/exercises.ts`, `src/data/exercises.more.ts` |
| Video sources and licence log | `src/data/videos.ts` |
| 12-week progression rules | `src/data/progression.ts` |
| Day + week -> flat step list, timing | `src/engine/compile.ts` |
| Single session clock (pause, skip, replay) | `src/engine/runner.ts` |
| Speech queue (browser text-to-speech) | `src/engine/speech.ts` |
| Progress saving (browser local storage) | `src/engine/storage.ts` |
| Player screen and controls | `src/player/` |

Checks (run with `node --experimental-strip-types scripts/<name>.ts`): `timing`, `progression-check`, `runner-test`, `coverage`, `list-clips`.

## Videos

All clips are played through YouTube's official embedded player, muted. Nothing is downloaded, merged or edited. Every clip is on the standard YouTube licence with embedding enabled by the owner; the log records creator, title, trim times and the date it was checked. A video can be removed or have embedding disabled at any time. The player then shows the exercise instructions as text and the session continues.

## Safety

Stop for sharp pain, dizziness, chest pain or unusual breathlessness. See a clinician for persistent or worsening upper-back pain, and before increasing intensity if pregnant, in fertility treatment, or advised to limit exercise. This app does not diagnose or treat any condition. It cannot target belly fat or cure PCOS.
