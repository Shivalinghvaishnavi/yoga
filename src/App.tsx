import { useState } from 'react'
import { schedule } from './data/schedule.ts'
import { paramsFor, phases } from './data/progression.ts'
import { Player } from './player/Player.tsx'
import Review from './Review.tsx'
import { loadProgress } from './engine/storage.ts'

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const WEEK_KEY = 'gf.weekOverride', START_KEY = 'gf.startDate'

// The week follows the calendar from the first launch. You can step it manually (e.g. repeat a week).
function initialWeek(): number {
  try {
    const override = Number(localStorage.getItem(WEEK_KEY))
    if (override >= 1 && override <= 12) return override
    const stored = localStorage.getItem(START_KEY) ?? String(Date.now())
    localStorage.setItem(START_KEY, stored)
    return Math.min(12, Math.floor((Date.now() - Number(stored)) / (7 * 864e5)) + 1)
  } catch { return 1 }
}

function Home() {
  const [active, setActive] = useState<{ day: number; from: number } | null>(null)
  const [week, setWeekState] = useState(initialWeek)
  const setWeek = (w: number) => {
    const next = Math.min(12, Math.max(1, w))
    setWeekState(next)
    try { localStorage.setItem(WEEK_KEY, String(next)) } catch { /* ignore */ }
  }
  if (active) return <Player day={active.day} week={week} resumeFrom={active.from} onExit={() => setActive(null)} />
  const p = paramsFor(week)
  return (
    <main className="home">
      <h1>My Guided Workout</h1>
      <div className="weekbar">
        <button onClick={() => setWeek(week - 1)} disabled={week <= 1} aria-label="Previous week">-</button>
        <div><strong>Week {week} of 12</strong><span>{p.phaseName}</span></div>
        <button onClick={() => setWeek(week + 1)} disabled={week >= 12} aria-label="Next week">+</button>
      </div>
      <p className="changes">{p.changes}</p>
      <ul className="days">
        {DAYS.map((name, i) => {
          const plan = schedule.find((d) => d.day === i)
          const saved = plan ? loadProgress(i, week) : null
          return (
            <li key={name} className={plan ? '' : 'soon'}>
              <div><strong>{name}</strong><span>{plan ? plan.title : 'Coming soon'}</span></div>
              {plan && <div className="actions">
                <button onClick={() => setActive({ day: i, from: 0 })}>Play</button>
                {saved && <button onClick={() => setActive({ day: i, from: saved.index })}>Resume</button>}
              </div>}
            </li>
          )
        })}
      </ul>
      <details className="plan">
        <summary>How the 12 weeks progress</summary>
        {phases.map((ph) => <p key={ph.name}><strong>{ph.name} (weeks {ph.weeks}).</strong> {ph.goal}</p>)}
        <p>Each two-week block changes one thing at a time: sets, then reps, then tube tension, then rep speed. Sessions stay near 45 minutes, so on strength days extra sets are balanced by a little less walking. Walking days (Tue, Thu, Sat) grow longer instead.</p>
        <p>Sunday stays a gentle recovery day in every week.</p>
      </details>
      <p className="safety">
        Stop if you feel sharp pain, dizziness, chest pain or unusual breathlessness. See a doctor or
        physiotherapist for persistent or worsening upper-back pain, and check with your clinician before
        increasing intensity if you are pregnant, having fertility treatment, or have been advised to limit
        exercise. This app is not medical advice and does not diagnose or treat any condition. Exercise
        supports overall health; it cannot target belly fat or cure PCOS.
      </p>
    </main>
  )
}

export default function App() {
  return new URLSearchParams(location.search).has('review') ? <Review /> : <Home />
}
