import type { Credentials, Token, User } from '../types'
import { api } from './client'

export const authApi = {
  register: (credentials: Credentials) => api.post<User>('/auth/register', credentials),
  login: (credentials: Credentials) => api.post<Token>('/auth/login', credentials),
  me: () => api.get<User>('/auth/me'),
  listUsers: () => api.get<User[]>('/users'),
}
