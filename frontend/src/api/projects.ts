import type { Project, ProjectCreateInput, ProjectInput } from '../types'
import { api } from './client'

export const projectsApi = {
  list: () => api.get<Project[]>('/projects'),
  get: (id: number) => api.get<Project>(`/projects/${id}`),
  create: (input: ProjectCreateInput) => api.post<Project>('/projects', input),
  update: (id: number, input: ProjectInput) => api.put<Project>(`/projects/${id}`, input),
  remove: (id: number) => api.delete(`/projects/${id}`),
}
