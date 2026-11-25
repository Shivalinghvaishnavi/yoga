import type { DayPlan, PlanItem, Section } from './types.ts'

// it(id, section, 'r'|'t', base, sets, rest): r = reps per set, t = seconds per set (per side if bilateral)
const it = (exerciseId: string, section: Section, m: 'r' | 't', base: number, baseSets = 1, restSec = 0): PlanItem =>
  ({ exerciseId, section, mode: m === 'r' ? 'reps' : 'timed', base, baseSets, restSec })

// Values are the Foundation (weeks 1-4) baseline. progression.ts adjusts them per week.
// Rest is taken after every set, so the last rest doubles as the transition to the next exercise.
export const schedule: DayPlan[] = [
  {
    day: 0,
    title: 'Lower Body + Core Strength',
    goals: ['Build leg and glute strength', 'Improve core stability', 'Support insulin sensitivity'],
    items: [
      { exerciseId: 'march', section: 'warmup', mode: 'timed', base: 150, baseSets: 1, restSec: 0 },
      { exerciseId: 'hip_circles', section: 'warmup', mode: 'timed', base: 90, baseSets: 1, restSec: 0 },
      { exerciseId: 'bw_squat', section: 'main', mode: 'reps', base: 10, baseSets: 2, restSec: 30 },
      { exerciseId: 'band_squat', section: 'main', mode: 'reps', base: 10, baseSets: 2, restSec: 45 },
      { exerciseId: 'band_rdl', section: 'main', mode: 'reps', base: 10, baseSets: 2, restSec: 45 },
      { exerciseId: 'glute_bridge', section: 'main', mode: 'reps', base: 12, baseSets: 2, restSec: 30 },
      { exerciseId: 'reverse_lunge', section: 'main', mode: 'reps', base: 8, baseSets: 2, restSec: 30 },
      { exerciseId: 'dead_bug', section: 'main', mode: 'reps', base: 8, baseSets: 2, restSec: 30 },
      { exerciseId: 'brisk_walk', section: 'cardio', mode: 'timed', base: 600, baseSets: 1, restSec: 0 },
      { exerciseId: 'lower_stretch', section: 'cooldown', mode: 'timed', base: 300, baseSets: 1, restSec: 0 },
      { exerciseId: 'breath_relax', section: 'relax', mode: 'timed', base: 300, baseSets: 1, restSec: 0 },
    ],
  },
  {
    day: 1, title: 'Yoga + Posture Correction',
    goals: ['Open the chest and ease rounded shoulders', 'Improve upper-back mobility', 'Reduce stress'],
    items: [
      it('gentle_breath', 'warmup', 't', 240), it('cat_cow', 'warmup', 't', 120),
      it('thread_needle', 'main', 't', 60, 2, 10), it('thoracic_ext_towel', 'main', 't', 90, 2, 15),
      it('wall_angels', 'main', 'r', 10, 2, 30), it('chin_tucks', 'main', 'r', 10, 2, 20),
      it('doorway_chest', 'main', 't', 60, 2, 15), it('childs_pose', 'cooldown', 't', 180),
      it('gentle_walk', 'cardio', 't', 660), it('breath_relax', 'relax', 't', 360),
    ],
  },
  {
    day: 2, title: 'Full-Body Resistance Training',
    goals: ['Strengthen the whole body', 'Build muscular endurance', 'Support insulin sensitivity'],
    items: [
      it('march', 'warmup', 't', 150), it('arm_circles', 'warmup', 't', 120),
      it('band_squat', 'main', 'r', 10, 2, 45), it('band_row', 'main', 'r', 10, 2, 45),
      it('wall_pushup', 'main', 'r', 8, 2, 30), it('band_curl', 'main', 'r', 10, 2, 30),
      it('band_pullapart', 'main', 'r', 12, 2, 30), it('bird_dog', 'main', 'r', 8, 2, 30),
      it('brisk_walk', 'cardio', 't', 600), it('full_stretch', 'cooldown', 't', 300), it('breath_relax', 'relax', 't', 300),
    ],
  },
  {
    day: 3, title: 'Walking + Recovery + Back Mobility',
    goals: ['Active recovery', 'Ease stress', 'Improve back and hip mobility'],
    items: [
      it('march', 'warmup', 't', 180), it('brisk_walk', 'cardio', 't', 1080),
      it('cat_cow', 'main', 't', 120), it('thoracic_rotation', 'main', 't', 60, 2, 10),
      it('shoulder_rolls', 'main', 't', 90), it('doorway_chest', 'main', 't', 45, 2, 15),
      it('hip_mobility', 'main', 't', 240), it('breath_relax', 'relax', 't', 420),
    ],
  },
  {
    day: 4, title: 'Lower Body + Upper-Back Strength',
    goals: ['Build leg, glute and hip strength', 'Strengthen the upper back', 'Improve posture'],
    items: [
      it('march', 'warmup', 't', 180), it('sit_to_stand', 'main', 'r', 10, 2, 30),
      it('band_deadlift', 'main', 'r', 10, 2, 40), it('band_row', 'main', 'r', 10, 2, 40),
      it('side_leg_raise', 'main', 'r', 8, 2, 20), it('pallof_press', 'main', 'r', 8, 2, 20),
      it('glute_bridge', 'main', 'r', 12, 2, 30), it('brisk_walk', 'cardio', 't', 720),
      it('lower_stretch', 'cooldown', 't', 300), it('breath_relax', 'relax', 't', 300),
    ],
  },
  {
    day: 5, title: 'Low-Impact Cardio + Yoga',
    goals: ['Build cardiovascular endurance', 'Improve flexibility', 'Reduce stress'],
    items: [
      it('march', 'warmup', 't', 180), it('brisk_walk', 'cardio', 't', 420), it('low_impact_dance', 'cardio', 't', 600),
      it('side_stretch', 'main', 't', 45, 2, 5), it('low_lunge', 'main', 't', 60, 2, 5),
      it('butterfly', 'main', 't', 120), it('seated_fold', 'main', 't', 120),
      it('hip_mobility', 'main', 't', 120), it('breath_relax', 'relax', 't', 420),
    ],
  },
  {
    day: 6, title: 'Restorative Yoga + Recovery',
    goals: ['Recover from the week', 'Release tension', 'Support mental well-being'],
    items: [
      it('gentle_walk', 'warmup', 't', 600), it('diaphragm_breath', 'warmup', 't', 300),
      it('cat_cow', 'main', 't', 180), it('childs_pose', 'main', 't', 240),
      it('supine_twist', 'main', 't', 150, 1, 5), it('neck_shoulder', 'main', 't', 240),
      it('body_scan', 'relax', 't', 660),
    ],
  },
]

