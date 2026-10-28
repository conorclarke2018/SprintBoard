import { Button, Group, Paper, Progress, Stack, Table, Text, Title, Tooltip } from '@mantine/core'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { sprintsApi } from '../api/sprints'
import { ConfirmModal } from '../components/ConfirmModal'
import { SprintStatusBadge } from '../components/IssueBadges'
import { PageLoader } from '../components/PageLoader'
import { useCurrentProject } from '../components/ProjectLayout'
import { SprintFormModal } from '../components/SprintFormModal'
import { useProjectData } from '../hooks/useProjectData'
import type { Sprint } from '../types'
import { formatDate } from '../utils/constants'
import { notifyError, notifySuccess } from '../utils/notify'

export function SprintsPage() {
  const project = useCurrentProject()
  const { sprints, activeSprint, loading, reload } = useProjectData(project.id)
  const [formOpen, setFormOpen] = useState(false)
  const [completing, setCompleting] = useState<Sprint | null>(null)

  if (loading) return <PageLoader />

  async function startSprint(sprint: Sprint) {
    try {
      await sprintsApi.start(sprint.id)
      notifySuccess(`${sprint.name} started. Good luck!`)
      await reload()
    } catch (error) {
      notifyError(error)
    }
  }

  async function completeSprint(sprint: Sprint) {
    const result = await sprintsApi.complete(sprint.id)
    const returned = result.returned_to_backlog
    notifySuccess(
      returned === 0
        ? `${sprint.name} completed with every issue done`
        : `${sprint.name} completed. ${returned} unfinished ${returned === 1 ? 'issue' : 'issues'} returned to the backlog`,
    )
    await reload()
  }

  const unfinished = completing ? completing.issue_count - completing.done_count : 0

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={3}>Sprints</Title>
        <Button onClick={() => setFormOpen(true)}>New sprint</Button>
      </Group>

      {sprints.length === 0 ? (
        <Paper withBorder p="xl" ta="center">
          <Text fw={500}>No sprints yet</Text>
          <Text c="dimmed" size="sm">
            A sprint is a short, fixed period of work, usually one or two weeks.
          </Text>
        </Paper>
      ) : (
        <Table.ScrollContainer minWidth={700}>
          <Table verticalSpacing="sm">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Sprint</Table.Th>
                <Table.Th>Dates</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th w={180}>Progress</Table.Th>
                <Table.Th w={200} />
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {sprints.map((sprint) => (
                <Table.Tr key={sprint.id}>
                  <Table.Td>
                    <Text fw={500}>{sprint.name}</Text>
                    {sprint.goal && (
                      <Text size="sm" c="dimmed" lineClamp={1}>
                        {sprint.goal}
                      </Text>
                    )}
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">
                      {formatDate(sprint.start_date)} – {formatDate(sprint.end_date)}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <SprintStatusBadge status={sprint.status} />
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="dimmed">
                      {sprint.done_count} of {sprint.issue_count} done
                    </Text>
                    <Progress
                      value={sprint.issue_count ? (sprint.done_count / sprint.issue_count) * 100 : 0}
                      color="green"
                      size="sm"
                    />
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs" justify="flex-end">
                      {sprint.status === 'planned' && (
                        <Button size="xs" variant="default" component={Link} to="../backlog">
                          Add issues
                        </Button>
                      )}
                      {sprint.status === 'planned' && (
                        <Tooltip
                          label={`Complete ${activeSprint?.name} first`}
                          disabled={!activeSprint}
                        >
                          <Button size="xs" disabled={Boolean(activeSprint)} onClick={() => startSprint(sprint)}>
                            Start sprint
                          </Button>
                        </Tooltip>
                      )}
                      {sprint.status === 'active' && (
                        <>
                          <Button size="xs" variant="default" component={Link} to="../board">
                            View board
                          </Button>
                          <Button size="xs" color="green" onClick={() => setCompleting(sprint)}>
                            Complete
                          </Button>
                        </>
                      )}
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      )}

      <SprintFormModal
        opened={formOpen}
        projectId={project.id}
        suggestedName={`Sprint ${sprints.length + 1}`}
        onClose={() => setFormOpen(false)}
        onSaved={reload}
      />
      <ConfirmModal
        opened={completing !== null}
        title={`Complete ${completing?.name ?? 'sprint'}?`}
        message={
          unfinished === 0
            ? 'Every issue in this sprint is done.'
            : `${unfinished} unfinished ${unfinished === 1 ? 'issue' : 'issues'} will return to the backlog.`
        }
        confirmLabel="Complete sprint"
        color="green"
        onConfirm={() => completeSprint(completing!)}
        onClose={() => setCompleting(null)}
      />
    </Stack>
  )
}
