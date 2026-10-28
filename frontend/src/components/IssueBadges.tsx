import { Badge } from '@mantine/core'
import type { IssuePriority, IssueStatus, IssueType, ProjectStatus, SprintStatus } from '../types'
import {
  PRIORITY_OPTIONS,
  PROJECT_STATUS_OPTIONS,
  SPRINT_STATUS_OPTIONS,
  STATUS_OPTIONS,
  TYPE_OPTIONS,
  findOption,
} from '../utils/constants'

export function StatusBadge({ status }: { status: IssueStatus }) {
  const option = findOption(STATUS_OPTIONS, status)
  return <Badge color={option.color} variant="light">{option.label}</Badge>
}

export function TypeBadge({ type }: { type: IssueType }) {
  const option = findOption(TYPE_OPTIONS, type)
  return <Badge color={option.color} variant="dot">{option.label}</Badge>
}

export function PriorityBadge({ priority }: { priority: IssuePriority }) {
  const option = findOption(PRIORITY_OPTIONS, priority)
  return <Badge color={option.color} variant="outline">{option.label}</Badge>
}

export function SprintStatusBadge({ status }: { status: SprintStatus }) {
  const option = findOption(SPRINT_STATUS_OPTIONS, status)
  return <Badge color={option.color} variant="light">{option.label}</Badge>
}

export function PointsBadge({ points }: { points: number | null }) {
  if (points === null) return null
  return (
    <Badge color="gray" variant="filled" radius="xl" title="Story points">
      {points}
    </Badge>
  )
}

export function ProjectStatusBadge({ status }: { status: ProjectStatus }) {
  const option = findOption(PROJECT_STATUS_OPTIONS, status)
  return <Badge color={option.color} variant="light">{option.label}</Badge>
}
