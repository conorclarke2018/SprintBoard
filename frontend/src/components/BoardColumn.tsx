import { useDraggable, useDroppable } from '@dnd-kit/core'
import { Badge, Group, Paper, Stack, Text } from '@mantine/core'
import type { Issue, IssueStatus } from '../types'
import { IssueCard } from './IssueCard'

interface BoardColumnProps {
  status: IssueStatus
  label: string
  color: string
  issues: Issue[]
  onEdit: (issue: Issue) => void
  onMove: (issue: Issue, status: IssueStatus) => void
}

export function BoardColumn({ status, label, color, issues, onEdit, onMove }: BoardColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id: status })

  return (
    <Paper
      ref={setNodeRef}
      withBorder
      p="sm"
      radius="md"
      bg={isOver ? 'var(--mantine-primary-color-light)' : 'var(--mantine-color-default-hover)'}
      style={{
        minHeight: 240,
        borderColor: isOver ? 'var(--mantine-primary-color-filled)' : undefined,
        transition: 'background-color 120ms, border-color 120ms',
      }}
    >
      <Group justify="space-between" mb="sm">
        <Text fw={600} size="sm" tt="uppercase">
          {label}
        </Text>
        <Badge color={color} variant="light" circle>
          {issues.length}
        </Badge>
      </Group>
      <Stack gap="sm">
        {issues.length === 0 ? (
          <Text size="sm" c="dimmed" ta="center" py="md">
            {isOver ? 'Drop here' : 'No issues'}
          </Text>
        ) : (
          issues.map((issue) => (
            <DraggableIssueCard key={issue.id} issue={issue} onEdit={onEdit} onMove={onMove} />
          ))
        )}
      </Stack>
    </Paper>
  )
}

function DraggableIssueCard({ issue, onEdit, onMove }: Omit<BoardColumnProps, 'status' | 'label' | 'color' | 'issues'> & { issue: Issue }) {
  const { setNodeRef, attributes, listeners, isDragging } = useDraggable({
    id: issue.id,
    data: { issue },
  })

  return (
    <div
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      aria-label={`${issue.key}: ${issue.title}. Press space to pick up and move.`}
      // While dragging, the copy in the DragOverlay follows the pointer; this one stays as a placeholder.
      style={{ opacity: isDragging ? 0.4 : 1, cursor: 'grab', touchAction: 'manipulation' }}
    >
      <IssueCard issue={issue} onEdit={onEdit} onMove={onMove} />
    </div>
  )
}
