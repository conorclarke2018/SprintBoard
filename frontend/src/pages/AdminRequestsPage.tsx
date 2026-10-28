import { Badge, Button, Card, Group, Modal, Paper, SimpleGrid, Stack, Text, Textarea, Title } from '@mantine/core'
import { useCallback, useEffect, useState } from 'react'
import { adminApi } from '../api/admin'
import { PageLoader } from '../components/PageLoader'
import { REQUESTS_CHANGED_EVENT } from '../hooks/usePendingCounts'
import type { Project } from '../types'
import { formatDate } from '../utils/constants'
import { notifyError, notifySuccess } from '../utils/notify'

export function AdminRequestsPage() {
  const [requests, setRequests] = useState<Project[] | null>(null)
  const [rejecting, setRejecting] = useState<Project | null>(null)
  const [reason, setReason] = useState('')
  const [busyId, setBusyId] = useState<number | null>(null)

  const loadRequests = useCallback(() => {
    adminApi
      .listProjectRequests()
      .then(setRequests)
      .catch((error) => {
        notifyError(error)
        setRequests([])
      })
  }, [])

  useEffect(loadRequests, [loadRequests])

  async function review(project: Project, action: () => Promise<Project>, message: string) {
    setBusyId(project.id)
    try {
      await action()
      notifySuccess(message)
      setRejecting(null)
      loadRequests()
      window.dispatchEvent(new Event(REQUESTS_CHANGED_EVENT))
    } catch (error) {
      notifyError(error)
    } finally {
      setBusyId(null)
    }
  }

  function openReject(project: Project) {
    setReason('')
    setRejecting(project)
  }

  if (requests === null) return <PageLoader />

  return (
    <Stack>
      <div>
        <Title order={2}>Project requests</Title>
        <Text c="dimmed" size="sm">
          Users' new projects wait here until an admin approves or rejects them.
        </Text>
      </div>

      {requests.length === 0 ? (
        <Paper withBorder p="xl" ta="center">
          <Text fw={500}>No requests waiting</Text>
          <Text c="dimmed" size="sm">
            New project requests from users will appear here.
          </Text>
        </Paper>
      ) : (
        <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }}>
          {requests.map((project) => (
            <Card key={project.id} withBorder radius="md" padding="lg">
              <Stack gap="xs" h="100%">
                <Group justify="space-between" wrap="nowrap">
                  <Title order={4} lineClamp={1}>
                    {project.name}
                  </Title>
                  <Badge variant="light">{project.key}</Badge>
                </Group>
                <Text size="sm" c="dimmed" style={{ flexGrow: 1 }}>
                  {project.description ?? 'No description'}
                </Text>
                <Text size="sm">
                  Requested by <strong>{project.owner.username}</strong> on{' '}
                  {formatDate(project.created_at.slice(0, 10))}
                </Text>
                <Group gap="xs" mt="xs">
                  <Button
                    size="xs"
                    color="green"
                    loading={busyId === project.id && rejecting === null}
                    onClick={() =>
                      review(project, () => adminApi.approveProject(project.id), `${project.key} approved`)
                    }
                  >
                    Approve
                  </Button>
                  <Button size="xs" variant="light" color="red" onClick={() => openReject(project)}>
                    Reject
                  </Button>
                </Group>
              </Stack>
            </Card>
          ))}
        </SimpleGrid>
      )}

      <Modal opened={rejecting !== null} onClose={() => setRejecting(null)} title={`Reject ${rejecting?.name ?? ''}?`}>
        <Stack>
          <Textarea
            label="Reason"
            description="Optional. The user will see this and can edit their request and resubmit it."
            autosize
            minRows={2}
            maxLength={300}
            value={reason}
            onChange={(event) => setReason(event.currentTarget.value)}
            data-autofocus
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setRejecting(null)}>
              Cancel
            </Button>
            <Button
              color="red"
              loading={busyId !== null}
              onClick={() =>
                rejecting &&
                review(
                  rejecting,
                  () => adminApi.rejectProject(rejecting.id, reason.trim() || null),
                  `${rejecting.key} rejected`,
                )
              }
            >
              Reject request
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  )
}
