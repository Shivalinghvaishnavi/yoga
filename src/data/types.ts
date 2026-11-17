export type Mode = 'reps' | 'timed'
export type Section = 'warmup' | 'main' | 'cardio' | 'cooldown' | 'relax'

export interface Exercise {
  id: string
  name: string
  equipment: string
  setup: string[]      // starting position, spoken before the exercise
  how: string[]        // how to perform
  posture: string[]    // posture cues, also spoken during work
  breathing: string
  mistakes: string[]
  easier: string
  bilateral?: boolean  // true = repeat per side (left then right)
  videoId?: string     // key into videos.json
}

// One line of a day plan. Week-dependent numbers live in progression.ts.
export interface PlanItem {
  exerciseId: string
  section: Section
  mode: Mode
  base: number         // reps per set, or seconds per set/hold
  baseSets: number
  restSec: number
}

export interface DayPlan {
  day: number          // 0 = Monday
  title: string
  goals: string[]
  items: PlanItem[]
}

// Flat, week-resolved unit the player executes.
export interface Step {
  kind: 'brief' | 'work' | 'rest'
  exerciseId: string
  section: Section
  mode: Mode
  target: number       // reps or seconds
  set: number
  totalSets: number
  side?: 'left' | 'right'
  tempo: number        // seconds per rep this week
  resistance?: string  // 'light' | 'medium' for tube exercises
  durationSec: number  // planned time, used for progress
}
