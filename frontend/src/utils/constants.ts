import type { IssuePriority, IssueStatus, IssueType, ProjectStatus, SprintStatus } from '../types'

interface Option<T extends string> {
  value: T
  label: string
  color: string
}

export const STATUS_OPTIONS: Option<IssueStatus>[] = [
  { value: 'todo', label: 'To Do', color: 'gray' },
  { value: 'in_progress', label: 'In Progress', color: 'blue' },
  { value: 'done', label: 'Done', color: 'green' },
]

export const TYPE_OPTIONS: Option<IssueType>[] = [
  { value: 'story', label: 'Story', color: 'teal' },
  { value: 'task', label: 'Task', color: 'indigo' },
  { value: 'bug', label: 'Bug', color: 'red' },
]

export const PRIORITY_OPTIONS: Option<IssuePriority>[] = [
  { value: 'low', label: 'Low', color: 'gray' },
  { value: 'medium', label: 'Medium', color: 'yellow' },
  { value: 'high', label: 'High', color: 'red' },
]

export const SPRINT_STATUS_OPTIONS: Option<SprintStatus>[] = [
  { value: 'planned', label: 'Planned', color: 'gray' },
  { value: 'active', label: 'Active', color: 'blue' },
  { value: 'completed', label: 'Completed', color: 'green' },
]

export const PROJECT_STATUS_OPTIONS: Option<ProjectStatus>[] = [
  { value: 'pending', label: 'Awaiting approval', color: 'yellow' },
  { value: 'approved', label: 'Approved', color: 'green' },
  { value: 'rejected', label: 'Rejected', color: 'red' },
]

export const STORY_POINT_OPTIONS = ['1', '2', '3', '5', '8', '13']

export function findOption<T extends string>(options: Option<T>[], value: T): Option<T> {
  return options.find((option) => option.value === value) ?? { value, label: value, color: 'gray' }
}

export function formatDate(isoDate: string): string {
  return new Date(`${isoDate}T00:00:00`).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function isoDate(daysFromToday = 0): string {
  const date = new Date()
  date.setDate(date.getDate() + daysFromToday)
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${month}-${day}`
}
