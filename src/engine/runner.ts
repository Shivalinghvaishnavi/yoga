import type { Step } from '../data/types.ts'

export type Status = 'idle' | 'running' | 'paused' | 'done'
export interface Snapshot { index: number; step: Step | null; elapsed: number; status: Status; token: number }

// Single clock for the whole session. UI and speech only react to snapshots.
// `token` changes on every step entry, so speech from an old step can be cancelled.
export class Runner {
  index = 0
  elapsed = 0
  status: Status = 'idle'
  token = 0
  speed = 1 // test aid only (?speed=10 in the URL); always 1 in normal use
  private speechDone = false
  private listeners = new Set<(s: Snapshot) => void>()
  private timer: ReturnType<typeof setInterval> | null = null

  steps: Step[]
  constructor(steps: Step[]) { this.steps = steps }

  get step(): Step | null { return this.steps[this.index] ?? null }
  snapshot(): Snapshot { return { index: this.index, step: this.step, elapsed: this.elapsed, status: this.status, token: this.token } }
  subscribe(fn: (s: Snapshot) => void) { this.listeners.add(fn); return () => this.listeners.delete(fn) }
  private emit() { const s = this.snapshot(); this.listeners.forEach((fn) => fn(s)) }

  private enter(index: number) {
    this.index = index; this.elapsed = 0; this.speechDone = false; this.token++
    if (index >= this.steps.length) { this.status = 'done'; this.stop() }
    this.emit()
  }

  start(from = 0) { this.enter(from); this.status = 'running'; this.emit(); this.timer ??= setInterval(() => this.tick(0.25 * this.speed), 250) }
  pause() { if (this.status === 'running') { this.status = 'paused'; this.emit() } }
  resume() { if (this.status === 'paused') { this.status = 'running'; this.emit() } }
  skip() { if (this.status !== 'done') this.enter(this.index + 1) }
  replay() { this.enter(this.index) } // restart the current step, new token silences old speech
  restart() { this.stop(); this.start(0) }
  stop() { if (this.timer) clearInterval(this.timer); this.timer = null }
  markSpeechDone() { this.speechDone = true }

  // A brief ends when its speech ends (with a safety cap); work and rest end on time alone.
  tick(dt: number) {
    const step = this.step
    if (this.status !== 'running' || !step) return
    this.elapsed += dt
    const finished = step.kind === 'brief'
      ? (this.speechDone && this.elapsed >= 1) || this.elapsed >= step.durationSec * 2
      : this.elapsed >= step.durationSec
    if (finished) this.enter(this.index + 1)
    else this.emit()
  }
}
