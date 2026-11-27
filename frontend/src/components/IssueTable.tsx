import { useDraggable } from '@dnd-kit/core'
import { Anchor, Button, Group, Select, Table, Text } from '@mantine/core'
import type { ReactNode } from 'react'
import type { Issue, Sprint } from '../types'
import { PointsBadge, PriorityBadge, StatusBadge, TypeBadge } from './IssueBadges'

interface IssueTableProps {
  issues: Issue[]
  sprints: Sprint[]
  emptyMessage: string
  onEdit: (issue: Issue) => void
  /** Only passed for admins, who are the only users allowed to delete. */
  onDelete?: (issue: Issue) => void
  onMoveToSprint: (issue: Issue, sprintId: number | null) => void
  /** Show the issues without any way to change them. */
  readOnly?: boolean
}

const BACKLOG_VALUE = 'backlog'

export function IssueTable({
  issues,
  sprints,
  emptyMessage,
  onEdit,
  onDelete,
  onMoveToSprint,
  readOnly = false,
}: IssueTableProps) {
  if (issues.length === 0) {
    return (
      <Text c="dimmed" size="sm" py="sm">
        {emptyMessage}
      </Text>
    )
  }

  const moveOptions = [
    { value: BACKLOG_VALUE, label: 'Backlog' },
    ...sprints
      .filter((sprint) => sprint.status !== 'completed')
      .map((sprint) => ({ value: String(sprint.id), label: sprint.name })),
  ]

  return (
    <Table.ScrollContainer minWidth={760}>
      <Table verticalSpacing="xs" highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            {!readOnly && <Table.Th w={28} />}
            <Table.Th w={80}>Key</Table.Th>
            <Table.Th>Title</Table.Th>
            <Table.Th w={90}>Type</Table.Th>
            <Table.Th w={90}>Priority</Table.Th>
            <Table.Th w={60}>Points</Table.Th>
            <Table.Th w={110}>Assignee</Table.Th>
            <Table.Th w={110}>Status</Table.Th>
            <Table.Th w={150}>Sprint</Table.Th>
            {onDelete && <Table.Th w={80} />}
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {issues.map((issue) => (
            <DraggableRow key={issue.id} issue={issue} disabled={readOnly}>
              {!readOnly && (
                <Table.Td c="dimmed" aria-hidden>
                  ⠿
                </Table.Td>
              )}
              <Table.Td>
                <Text size="sm" c="dimmed" ff="monospace">
                  {issue.key}
                </Text>
              </Table.Td>
              <Table.Td>
                {readOnly ? (
                  <Text size="sm">{issue.title}</Text>
                ) : (
                  <Anchor component="button" type="button" size="sm" onClick={() => onEdit(issue)} ta="left">
                    {issue.title}
                  </Anchor>
                )}
              </Table.Td>
              <Table.Td>
                <TypeBadge type={issue.type} />
              </Table.Td>
              <Table.Td>
                <PriorityBadge priority={issue.priority} />
              </Table.Td>
              <Table.Td>
                <PointsBadge points={issue.story_points} />
              </Table.Td>
              <Table.Td>
                <Text size="sm" c={issue.assignee ? undefined : 'dimmed'}>
                  {issue.assignee?.username ?? 'Unassigned'}
                </Text>
              </Table.Td>
              <Table.Td>
                <StatusBadge status={issue.status} />
              </Table.Td>
              <Table.Td>
                <Select
                  size="xs"
                  aria-label={`Move ${issue.key} to`}
                  data={moveOptions}
                  value={issue.sprint_id === null ? BACKLOG_VALUE : String(issue.sprint_id)}
                  allowDeselect={false}
                  disabled={readOnly}
                  onChange={(value) => {
                    if (!value) return
                    onMoveToSprint(issue, value === BACKLOG_VALUE ? null : Number(value))
                  }}
                />
              </Table.Td>
              {onDelete && (
                <Table.Td>
                  <Group gap={4} justify="flex-end" wrap="nowrap">
                    <Button size="compact-xs" variant="subtle" color="red" onClick={() => onDelete(issue)}>
                      Delete
                    </Button>
                  </Group>
                </Table.Td>
              )}
            </DraggableRow>
          ))}
        </Table.Tbody>
      </Table>
    </Table.ScrollContainer>
  )
}

function DraggableRow({ issue, disabled, children }: { issue: Issue; disabled: boolean; children: ReactNode }) {
  const { setNodeRef, attributes, listeners, isDragging } = useDraggable({
    id: issue.id,
    data: { issue },
    disabled,
  })

  if (disabled) return <Table.Tr>{children}</Table.Tr>

  return (
    <Table.Tr
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      aria-label={`${issue.key}: ${issue.title}. Press space to pick up and move.`}
      style={{ opacity: isDragging ? 0.4 : 1, cursor: 'grab', touchAction: 'manipulation' }}
    >
      {children}
    </Table.Tr>
  )
}
