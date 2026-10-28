import type { Issue, IssueInput, IssueUpdateInput } from '../types'
import { api } from './client'

export const issuesApi = {
  list: (projectId: number) => api.get<Issue[]>(`/projects/${projectId}/issues`),
  create: (projectId: number, input: IssueInput) =>
    api.post<Issue>(`/projects/${projectId}/issues`, input),
  update: (id: number, input: IssueUpdateInput) => api.put<Issue>(`/issues/${id}`, input),
  remove: (id: number) => api.delete(`/issues/${id}`),
}

export function toIssueUpdate(issue: Issue, changes: Partial<IssueUpdateInput> = {}): IssueUpdateInput {
  return {
    title: issue.title,
    description: issue.description,
    type: issue.type,
    priority: issue.priority,
    story_points: issue.story_points,
    assignee_id: issue.assignee?.id ?? null,
    sprint_id: issue.sprint_id,
    status: issue.status,
    ...changes,
  }
}
