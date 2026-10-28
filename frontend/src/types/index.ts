export type IssueType = 'story' | 'task' | 'bug'
export type IssueStatus = 'todo' | 'in_progress' | 'done'
export type IssuePriority = 'low' | 'medium' | 'high'
export type SprintStatus = 'planned' | 'active' | 'completed'
export type UserRole = 'user' | 'admin'
export type ProjectStatus = 'pending' | 'approved' | 'rejected'

export interface User {
  id: number
  username: string
  role: UserRole
  is_approved: boolean
}

export interface AdminUser extends User {
  created_at: string
  project_count: number
}

export interface Credentials {
  username: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
  user: User
}

export interface Project {
  id: number
  name: string
  key: string
  description: string | null
  status: ProjectStatus
  review_note: string | null
  created_at: string
  issue_count: number
  owner: User
}

export interface ProjectInput {
  name: string
  description: string | null
}

export interface ProjectCreateInput extends ProjectInput {
  key: string
}

export interface Sprint {
  id: number
  project_id: number
  name: string
  goal: string | null
  start_date: string
  end_date: string
  status: SprintStatus
  issue_count: number
  done_count: number
}

export interface SprintInput {
  name: string
  goal: string | null
  start_date: string
  end_date: string
}

export interface SprintCompleteResult {
  sprint: Sprint
  returned_to_backlog: number
}

export interface Issue {
  id: number
  key: string
  number: number
  project_id: number
  sprint_id: number | null
  title: string
  description: string | null
  type: IssueType
  status: IssueStatus
  priority: IssuePriority
  story_points: number | null
  assignee: User | null
  created_at: string
  updated_at: string
}

export interface IssueInput {
  title: string
  description: string | null
  type: IssueType
  priority: IssuePriority
  story_points: number | null
  assignee_id: number | null
  sprint_id: number | null
}

export interface IssueUpdateInput extends IssueInput {
  status: IssueStatus
}
