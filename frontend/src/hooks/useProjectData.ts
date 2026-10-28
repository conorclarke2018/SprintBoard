import { useCallback, useEffect, useState } from 'react'
import { authApi } from '../api/auth'
import { issuesApi, toIssueUpdate } from '../api/issues'
import { sprintsApi } from '../api/sprints'
import type { Issue, IssueUpdateInput, Sprint, User } from '../types'
import { notifyError, notifySuccess } from '../utils/notify'

export function useProjectData(projectId: number) {
  const [issues, setIssues] = useState<Issue[]>([])
  const [sprints, setSprints] = useState<Sprint[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)

  const reload = useCallback(async () => {
    try {
      const [loadedIssues, loadedSprints, loadedUsers] = await Promise.all([
        issuesApi.list(projectId),
        sprintsApi.list(projectId),
        authApi.listUsers(),
      ])
      setIssues(loadedIssues)
      setSprints(loadedSprints)
      setUsers(loadedUsers)
    } catch (error) {
      notifyError(error)
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    void reload()
  }, [reload])

  const updateIssue = useCallback(
    async (issue: Issue, changes: Partial<IssueUpdateInput>, successMessage: string) => {
      const { status, sprint_id } = changes
      setIssues((current) =>
        current.map((item) =>
          item.id === issue.id
            ? { ...item, status: status ?? item.status, sprint_id: sprint_id === undefined ? item.sprint_id : sprint_id }
            : item,
        ),
      )
      try {
        await issuesApi.update(issue.id, toIssueUpdate(issue, changes))
        notifySuccess(successMessage)
      } catch (error) {
        notifyError(error)
      }
      await reload()
    },
    [reload],
  )

  const activeSprint = sprints.find((sprint) => sprint.status === 'active') ?? null

  return { issues, sprints, users, activeSprint, loading, reload, updateIssue }
}
