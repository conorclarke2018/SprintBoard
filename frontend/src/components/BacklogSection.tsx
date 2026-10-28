import { useDroppable } from '@dnd-kit/core'
import { Paper } from '@mantine/core'
import type { ReactNode } from 'react'

interface BacklogSectionProps {
  sprintId: number | null
  children: ReactNode
}

// A sprint (or the backlog itself) that issues can be dropped into.
export function BacklogSection({ sprintId, children }: BacklogSectionProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: sprintId === null ? 'backlog' : `sprint-${sprintId}`,
    data: { sprintId },
  })

  return (
    <Paper
      ref={setNodeRef}
      withBorder
      p="md"
      radius="md"
      bg={isOver ? 'var(--mantine-primary-color-light)' : undefined}
      style={{
        borderColor: isOver ? 'var(--mantine-primary-color-filled)' : undefined,
        transition: 'background-color 120ms, border-color 120ms',
      }}
    >
      {children}
    </Paper>
  )
}
