import { DndContext, DragOverlay } from '@dnd-kit/core'
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core'
import { Button, Group, Paper, SimpleGrid, Stack, Text, Title } from '@mantine/core'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { BoardColumn } from '../components/BoardColumn'
import { IssueCard } from '../components/IssueCard'
import { IssueFormModal } from '../components/IssueFormModal'
import { PageLoader } from '../components/PageLoader'
import { useCurrentProject } from '../components/ProjectLayout'
import { useDragSensors } from '../hooks/useDragSensors'
import { useProjectData } from '../hooks/useProjectData'
import type { Issue, IssueStatus } from '../types'
import { STATUS_OPTIONS, findOption, formatDate } from '../utils/constants'

export function BoardPage() {
  const project = useCurrentProject()
  const { issues, sprints, users, activeSprint, loading, reload, updateIssue } = useProjectData(project.id)
  const [editing, setEditing] = useState<Issue | null>(null)
  const [dragged, setDragged] = useState<Issue | null>(null)

  const sensors = useDragSensors()

  if (loading) return <PageLoader />

  if (!activeSprint) {
    return (
      <Paper withBorder p="xl" ta="center">
        <Text fw={500}>No active sprint</Text>
        <Text c="dimmed" size="sm" mb="md">
          Start a sprint to see its issues on the board.
        </Text>
        <Button component={Link} to="../sprints">
          Go to sprints
        </Button>
      </Paper>
    )
  }

  const sprintIssues = issues.filter((issue) => issue.sprint_id === activeSprint.id)

  function moveIssue(issue: Issue, status: IssueStatus) {
    if (issue.status === status) return
    const label = findOption(STATUS_OPTIONS, status).label
    void updateIssue(issue, { status }, `${issue.key} moved to ${label}`)
  }

  function handleDragStart(event: DragStartEvent) {
    setDragged(event.active.data.current?.issue ?? null)
  }

  function handleDragEnd(event: DragEndEvent) {
    setDragged(null)
    const issue = event.active.data.current?.issue as Issue | undefined
    if (issue && event.over) moveIssue(issue, event.over.id as IssueStatus)
  }

  return (
    <Stack>
      <Group justify="space-between" align="flex-end">
        <div>
          <Title order={3}>{activeSprint.name}</Title>
          <Text size="sm" c="dimmed">
            {formatDate(activeSprint.start_date)} – {formatDate(activeSprint.end_date)}
            {activeSprint.goal && ` · Goal: ${activeSprint.goal}`}
          </Text>
        </div>
        <Button variant="default" component={Link} to="../sprints">
          Manage sprints
        </Button>
      </Group>

      <Text size="sm" c="dimmed">
        Drag a card to another column to change its status.
      </Text>

      <DndContext
        sensors={sensors}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        onDragCancel={() => setDragged(null)}
      >
        <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
          {STATUS_OPTIONS.map((column) => (
            <BoardColumn
              key={column.value}
              status={column.value}
              label={column.label}
              color={column.color}
              issues={sprintIssues.filter((issue) => issue.status === column.value)}
              onEdit={setEditing}
              onMove={moveIssue}
            />
          ))}
        </SimpleGrid>

        <DragOverlay>
          {dragged && (
            <div style={{ cursor: 'grabbing', transform: 'rotate(2deg)', boxShadow: 'var(--mantine-shadow-lg)' }}>
              <IssueCard issue={dragged} onEdit={() => {}} onMove={() => {}} />
            </div>
          )}
        </DragOverlay>
      </DndContext>

      <IssueFormModal
        opened={editing !== null}
        projectId={project.id}
        issue={editing}
        sprints={sprints}
        users={users}
        onClose={() => setEditing(null)}
        onSaved={reload}
      />
    </Stack>
  )
}
