import type { AdminUser, Project, UserRole } from '../types'
import { api } from './client'

export const adminApi = {
  listUsers: () => api.get<AdminUser[]>('/admin/users'),
  approveUser: (userId: number) => api.post<AdminUser>(`/admin/users/${userId}/approve`),
  setRole: (userId: number, role: UserRole) =>
    api.put<AdminUser>(`/admin/users/${userId}/role`, { role }),
  deleteUser: (userId: number) => api.delete(`/admin/users/${userId}`),
  listProjectRequests: () => api.get<Project[]>('/admin/project-requests'),
  approveProject: (projectId: number) => api.post<Project>(`/admin/projects/${projectId}/approve`),
  rejectProject: (projectId: number, reason: string | null) =>
    api.post<Project>(`/admin/projects/${projectId}/reject`, { reason }),
}
