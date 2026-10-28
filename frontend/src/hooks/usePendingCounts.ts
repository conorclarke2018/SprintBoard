import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { adminApi } from '../api/admin'

export const REQUESTS_CHANGED_EVENT = 'sprintboard:requests-changed'

interface PendingCounts {
  projects: number
  users: number
}

const NONE: PendingCounts = { projects: 0, users: 0 }

// Project requests and accounts waiting for an admin, refreshed on navigation and after a review.
export function usePendingCounts(enabled: boolean): PendingCounts {
  const [counts, setCounts] = useState(NONE)
  const location = useLocation()

  useEffect(() => {
    if (!enabled) return
    const refresh = () => {
      Promise.all([adminApi.listProjectRequests(), adminApi.listUsers()])
        .then(([projects, users]) =>
          setCounts({ projects: projects.length, users: users.filter((u) => !u.is_approved).length }),
        )
        .catch(() => setCounts(NONE))
    }
    refresh()
    window.addEventListener(REQUESTS_CHANGED_EVENT, refresh)
    return () => window.removeEventListener(REQUESTS_CHANGED_EVENT, refresh)
  }, [enabled, location.pathname])

  return enabled ? counts : NONE
}
