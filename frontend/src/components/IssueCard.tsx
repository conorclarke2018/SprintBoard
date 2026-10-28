import { Anchor, Button, Card, Group, Stack, Text } from '@mantine/core'
import type { Issue, IssueStatus } from '../types'
import { STATUS_OPTIONS } from '../utils/constants'
import { PointsBadge, PriorityBadge, TypeBadge } from './IssueBadges'

interface IssueCardProps {
  issue: Issue
  onEdit: (issue: Issue) => void
  onMove: (issue: Issue, status: IssueStatus) => void
}

export function IssueCard({ issue, onEdit, onMove }: IssueCardProps) {
  const index = STATUS_OPTIONS.findIndex((option) => option.value === issue.status)
  const previous = STATUS_OPTIONS[index - 1]
  const next = STATUS_OPTIONS[index + 1]

  return (
    <Card withBorder padding="sm" radius="md">
      <Stack gap={6}>
        <Group justify="space-between" wrap="nowrap">
          <Text size="xs" c="dimmed" ff="monospace">
            {issue.key}
          </Text>
          <TypeBadge type={issue.type} />
        </Group>

        <Anchor component="button" type="button" fw={500} size="sm" ta="left" c="inherit" onClick={() => onEdit(issue)}>
          {issue.title}
        </Anchor>

        <Group gap={6}>
          <PriorityBadge priority={issue.priority} />
          <PointsBadge points={issue.story_points} />
          <Text size="xs" c="dimmed" ml="auto">
            {issue.assignee?.username ?? 'Unassigned'}
          </Text>
        </Group>

        <Group gap={6} justify="space-between">
          {previous ? (
            <Button size="compact-xs" variant="default" onClick={() => onMove(issue, previous.value)}>
              ← {previous.label}
            </Button>
          ) : (
            <span />
          )}
          {next && (
            <Button size="compact-xs" variant="light" onClick={() => onMove(issue, next.value)}>
              {next.label} →
            </Button>
          )}
        </Group>
      </Stack>
    </Card>
  )
}
