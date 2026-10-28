import { Badge, Button, Card, Group, Paper, SimpleGrid, Stack, Text, Title } from '@mantine/core'
import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectsApi } from '../api/projects'
import { ConfirmModal } from '../components/ConfirmModal'
import { ProjectStatusBadge } from '../components/IssueBadges'
import { PageLoader } from '../components/PageLoader'
import { ProjectFormModal } from '../components/ProjectFormModal'
import { useAuth } from '../context/AuthContext'
import type { Project } from '../types'
import { notifyError, notifySuccess } from '../utils/notify'

export function ProjectsPage() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const [projects, setProjects] = useState<Project[] | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Project | null>(null)
  const [deleting, setDeleting] = useState<Project | null>(null)

  const loadProjects = useCallback(() => {
    projectsApi
      .list()
      .then(setProjects)
      .catch((error) => {
        notifyError(error)
        setProjects([])
      })
  }, [])

  useEffect(loadProjects, [loadProjects])

  function openForm(project: Project | null) {
    setEditing(project)
    setFormOpen(true)
  }

  async function deleteProject(project: Project) {
    await projectsApi.remove(project.id)
    notifySuccess(`Project ${project.key} deleted`)
    loadProjects()
  }

  if (projects === null) return <PageLoader />

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={2}>{isAdmin ? 'All projects' : 'Projects'}</Title>
        <Button onClick={() => openForm(null)}>{isAdmin ? 'New project' : 'Request project'}</Button>
      </Group>

      {projects.length === 0 ? (
        <Paper withBorder p="xl" ta="center">
          <Text fw={500}>No projects yet</Text>
          <Text c="dimmed" size="sm" mb="md">
            {isAdmin
              ? 'Create your first project to start adding issues and sprints.'
              : 'Request a project. Once an admin approves it you can add issues and sprints.'}
          </Text>
          <Button onClick={() => openForm(null)}>{isAdmin ? 'Create a project' : 'Request a project'}</Button>
        </Paper>
      ) : (
        <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }}>
          {projects.map((project) => (
            <Card key={project.id} withBorder radius="md" padding="lg">
              <Stack gap="xs" h="100%">
                <Group justify="space-between" wrap="nowrap">
                  <Title order={4} lineClamp={1}>
                    {project.name}
                  </Title>
                  <Badge variant="light">{project.key}</Badge>
                </Group>
                {project.status !== 'approved' && <ProjectStatusBadge status={project.status} />}
                {project.status === 'rejected' && project.review_note && (
                  <Text size="sm" c="red">
                    Reason: {project.review_note}
                  </Text>
                )}
                <Text size="sm" c="dimmed" lineClamp={2} style={{ flexGrow: 1 }}>
                  {project.description ?? 'No description'}
                </Text>
                <Text size="sm">
                  {project.issue_count} {project.issue_count === 1 ? 'issue' : 'issues'}
                  {project.owner.id !== user?.id && (
                    <Text span c="dimmed" size="sm">
                      {' '}
                      · Owner: {project.owner.username}
                    </Text>
                  )}
                </Text>
                <Group gap="xs" mt="xs">
                  {project.status === 'approved' && (
                    <Button component={Link} to={`/projects/${project.id}/backlog`} size="xs">
                      Open
                    </Button>
                  )}
                  {project.status === 'pending' && isAdmin && (
                    <Button component={Link} to="/admin/requests" size="xs" color="yellow">
                      Review
                    </Button>
                  )}
                  <Button size="xs" variant="default" onClick={() => openForm(project)}>
                    {project.status === 'rejected' && !isAdmin ? 'Edit & resubmit' : 'Edit'}
                  </Button>
                  <Button size="xs" variant="subtle" color="red" onClick={() => setDeleting(project)}>
                    Delete
                  </Button>
                </Group>
              </Stack>
            </Card>
          ))}
        </SimpleGrid>
      )}

      <ProjectFormModal
        opened={formOpen}
        project={editing}
        onClose={() => setFormOpen(false)}
        onSaved={loadProjects}
      />
      <ConfirmModal
        opened={deleting !== null}
        title="Delete project?"
        message={`This permanently deletes ${deleting?.name ?? ''} and all of its issues and sprints.`}
        confirmLabel="Delete project"
        onConfirm={() => deleteProject(deleting!)}
        onClose={() => setDeleting(null)}
      />
    </Stack>
  )
}
