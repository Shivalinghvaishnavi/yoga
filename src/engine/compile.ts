import type { DayPlan, Exercise, PlanItem, Step } from '../data/types.ts'
import { exercises } from '../data/exercises.ts'
import { KEY_LIFTS, WALK_DAYS, paramsFor, type WeekParams } from '../data/progression.ts'

const WORDS_PER_SEC = 2.4 // calm speaking pace
const TARGET_MIN = 43 * 60, TARGET_MAX = 47 * 60 // sessions stay "about 45 minutes"

const hasTube = (e: Exercise) => e.equipment.includes('Tube band')

// `coaching` adds the easier-version line; used in the Foundation weeks, then dropped to keep sessions near 45 minutes.
export function briefText(e: Exercise, resistance?: string, coaching = true): string[] {
  const tension = hasTube(e) && resistance ? [`Use ${resistance} tension.`] : []
  return [e.name + '.', ...tension, ...e.setup, ...e.how, ...e.posture, e.breathing, ...(coaching ? [`If it feels too hard: ${e.easier}`] : [])]
}

function briefSec(e: Exercise, resistance?: string, coaching = true): number {
  return Math.ceil(briefText(e, resistance, coaching).join(' ').split(/\s+/).length / WORDS_PER_SEC) + 2
}

function applyWeek(plan: DayPlan, p: WeekParams): PlanItem[] {
  return plan.items.map((it) => {
    const next = { ...it }
    if (it.mode === 'reps') {
      next.base = it.base + p.repsAdd
      if (p.extraSet && KEY_LIFTS.has(it.exerciseId)) next.baseSets = it.baseSets + 1
    } else if (it.section === 'cardio' && WALK_DAYS.has(plan.day)) {
      next.base = it.base + p.walkAdd
    }
    return next
  })
}

function build(items: PlanItem[], p: WeekParams): Step[] {
  const steps: Step[] = []
  for (const item of items) {
    const ex = exercises[item.exerciseId]
    const resistance = hasTube(ex) ? p.resistance : undefined
    const sides: Array<'left' | 'right' | undefined> = ex.bilateral ? ['left', 'right'] : [undefined]
    const base = { exerciseId: ex.id, section: item.section, mode: item.mode, target: item.base, totalSets: item.baseSets, tempo: p.tempoSec, resistance }
    steps.push({ ...base, kind: 'brief', set: 1, durationSec: briefSec(ex, resistance, p.phase === 1) })
    for (let set = 1; set <= item.baseSets; set++) {
      for (const side of sides) {
        const dur = item.mode === 'reps' ? item.base * p.tempoSec : item.base
        steps.push({ ...base, kind: 'work', set, side, durationSec: dur })
      }
      if (item.restSec > 0) steps.push({ ...base, kind: 'rest', set, durationSec: item.restSec })
    }
  }
  return steps
}

export function totalSec(steps: Step[]): number {
  return steps.reduce((sum, s) => sum + s.durationSec, 0)
}

// Compiles one day for a given week. If extra work pushes the session past ~47 minutes,
// cardio is shortened in 30 s steps (never below 50% of its base) so the session stays near 45.
export function compileDay(plan: DayPlan, week = 1): Step[] {
  const p = paramsFor(week)
  const items = applyWeek(plan, p)
  let steps = build(items, p)
  const floor = new Map(items.map((it, i) => [i, it.section === 'cardio' ? Math.round(it.base * 0.5) : it.base]))
  for (let guard = 0; guard < 200 && totalSec(steps) > TARGET_MAX; guard++) {
    const idx = items.findIndex((it, i) => it.section === 'cardio' && it.base - 30 >= (floor.get(i) ?? 0))
    if (idx < 0) break
    items[idx] = { ...items[idx], base: items[idx].base - 30 }
    steps = build(items, p)
  }
  return steps
}

export { TARGET_MIN, TARGET_MAX }
