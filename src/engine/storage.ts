const KEY = 'gf.progress'
export interface Progress { day: number; week: number; index: number; savedAt: number }

export function saveProgress(p: Progress) {
  try { localStorage.setItem(KEY, JSON.stringify(p)) } catch { /* private mode: resume just won't work */ }
}

export function loadProgress(day: number, week: number): Progress | null {
  try {
    const p = JSON.parse(localStorage.getItem(KEY) ?? 'null') as Progress | null
    const fresh = p && Date.now() - p.savedAt < 24 * 3600 * 1000 // ignore yesterday's session
    return p && p.day === day && p.week === week && fresh ? p : null
  } catch { return null }
}

export function clearProgress() {
  try { localStorage.removeItem(KEY) } catch { /* ignore */ }
}
