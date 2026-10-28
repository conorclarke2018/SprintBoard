import type { Sprint, SprintCompleteResult, SprintInput } from '../types'
import { api } from './client'

export const sprintsApi = {
  list: (projectId: number) => api.get<Sprint[]>(`/projects/${projectId}/sprints`),
  create: (projectId: number, input: SprintInput) =>
    api.post<Sprint>(`/projects/${projectId}/sprints`, input),
  start: (id: number) => api.post<Sprint>(`/sprints/${id}/start`),
  complete: (id: number) => api.post<SprintCompleteResult>(`/sprints/${id}/complete`),
}
