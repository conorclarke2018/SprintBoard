import { DndContext, DragOverlay } from '@dnd-kit/core'
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core'
import { Button, Group, Paper, Stack, Text, Title } from '@mantine/core'
import { useState } from 'react'
import { issuesApi } from '../api/issues'
import { BacklogSection } from '../components/BacklogSection'
import { ConfirmModal } from '../components/ConfirmModal'
import { SprintStatusBadge, TypeBadge } from '../components/IssueBadges'
import { IssueFormModal } from '../components/IssueFormModal'
import { IssueTable } from '../components/IssueTable'
import { PageLoader } from '../components/PageLoader'
import { useCurrentProject } from '../components/ProjectLayout'
import { useDragSensors } from '../hooks/useDragSensors'
import { useProjectData } from '../hooks/useProjectData'
import type { Issue } from '../types'
import { formatDate } from '../utils/constants'
import { notifySuccess } from '../utils/notify'

export function BacklogPage() {
  const project = useCurrentProject()
  const { issues, sprints, users, loading, reload, updateIssue } = useProjectData(project.id)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Issue | null>(null)
  const [deleting, setDeleting] = useState<Issue | null>(null)
  const [dragged, setDragged] = useState<Issue | null>(null)
  const sensors = useDragSensors()

  if (loading) return <PageLoader />

  const openSprints = sprints.filter((sprint) => sprint.status !== 'completed')
  const backlog = issues.filter((issue) => issue.sprint_id === null)

  function openForm(issue: Issue | null) {
    setEditing(issue)
    setFormOpen(true)
  }

  function moveToSprint(issue: Issue, sprintId: number | null) {
    if (issue.sprint_id === sprintId) return
    const sprint = sprints.find((s) => s.id === sprintId)
    const message = sprint ? `${issue.key} moved to ${sprint.name}` : `${issue.key} moved to the backlog`
    void updateIssue(issue, { sprint_id: sprintId }, message)
  }

  function handleDragStart(event: DragStartEvent) {
    setDragged(event.active.data.current?.issue ?? null)
  }

  function handleDragEnd(event: DragEndEvent) {
    setDragged(null)
    const issue = event.active.data.current?.issue as Issue | undefined
    const target = event.over?.data.current as { sprintId: number | null } | undefined
    if (issue && target) moveToSprint(issue, target.sprintId)
  }

  async function deleteIssue(issue: Issue) {
    await issuesApi.remove(issue.id)
    notifySuccess(`${issue.key} deleted`)
    await reload()
  }

  const tableProps = { sprints, onEdit: openForm, onDelete: setDeleting, onMoveToSprint: moveToSprint }

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={3}>Backlog</Title>
        <Button onClick={() => openForm(null)}>Create issue</Button>
      </Group>

      <Text size="sm" c="dimmed">
        Drag issues between the backlog and any planned or active sprint to plan your work.
      </Text>

      <DndContext
        sensors={sensors}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        onDragCancel={() => setDragged(null)}
      >
        {openSprints.map((sprint) => (
          <BacklogSection key={sprint.id} sprintId={sprint.id}>
            <Group gap="sm" mb="xs">
              <Text fw={600}>{sprint.name}</Text>
              <SprintStatusBadge status={sprint.status} />
              <Text size="sm" c="dimmed">
                {formatDate(sprint.start_date)} – {formatDate(sprint.end_date)}
              </Text>
            </Group>
            {sprint.goal && (
              <Text size="sm" c="dimmed" mb="xs">
                Goal: {sprint.goal}
              </Text>
            )}
            <IssueTable
              issues={issues.filter((issue) => issue.sprint_id === sprint.id)}
              emptyMessage="No issues in this sprint yet. Drag issues here from the backlog."
              {...tableProps}
            />
          </BacklogSection>
        ))}

        <BacklogSection sprintId={null}>
          <Group gap="sm" mb="xs">
            <Text fw={600}>Backlog</Text>
            <Text size="sm" c="dimmed">
              {backlog.length} {backlog.length === 1 ? 'issue' : 'issues'}
            </Text>
          </Group>
          {openSprints.length === 0 && (
            <Text size="sm" c="dimmed" mb="xs">
              Tip: create a sprint on the Sprints tab, then move issues into it.
            </Text>
          )}
          <IssueTable issues={backlog} emptyMessage="The backlog is empty. Create an issue to get started." {...tableProps} />
        </BacklogSection>

        <DragOverlay>
          {dragged && (
            <Paper withBorder shadow="lg" p="xs" radius="md" maw={420} style={{ cursor: 'grabbing' }}>
              <Group gap="sm" wrap="nowrap">
                <Text size="sm" c="dimmed" ff="monospace">
                  {dragged.key}
                </Text>
                <Text size="sm" fw={500} lineClamp={1}>
                  {dragged.title}
                </Text>
                <TypeBadge type={dragged.type} />
              </Group>
            </Paper>
          )}
        </DragOverlay>
      </DndContext>

      <IssueFormModal
        opened={formOpen}
        projectId={project.id}
        issue={editing}
        sprints={sprints}
        users={users}
        onClose={() => setFormOpen(false)}
        onSaved={reload}
      />
      <ConfirmModal
        opened={deleting !== null}
        title="Delete issue?"
        message={`${deleting?.key ?? ''} "${deleting?.title ?? ''}" will be permanently deleted.`}
        confirmLabel="Delete issue"
        onConfirm={() => deleteIssue(deleting!)}
        onClose={() => setDeleting(null)}
      />
    </Stack>
  )
}
