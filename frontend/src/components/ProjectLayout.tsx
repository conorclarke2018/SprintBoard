import { Alert, Anchor, Badge, Breadcrumbs, Group, Stack, Tabs, Text, Title } from '@mantine/core'
import { useCallback, useEffect, useState } from 'react'
import { Link, Outlet, useLocation, useNavigate, useOutletContext, useParams } from 'react-router-dom'
import { ApiError } from '../api/client'
import { projectsApi } from '../api/projects'
import type { Project } from '../types'
import { PageLoader } from './PageLoader'

interface ProjectOutletContext {
  project: Project
}

const TABS = [
  { value: 'backlog', label: 'Backlog' },
  { value: 'sprints', label: 'Sprints' },
  { value: 'board', label: 'Board' },
]

export function ProjectLayout() {
  const { projectId } = useParams()
  const id = Number(projectId)
  const validId = Number.isInteger(id)
  const navigate = useNavigate()
  const location = useLocation()
  const [project, setProject] = useState<Project | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const error = validId ? loadError : 'Project not found'

  const loadProject = useCallback(() => {
    if (!validId) return
    projectsApi
      .get(id)
      .then(setProject)
      .catch((err) => setLoadError(err instanceof ApiError ? err.message : 'Could not load the project'))
  }, [id, validId])

  useEffect(loadProject, [loadProject])

  if (error) {
    return (
      <Alert color="red" title="Something went wrong">
        {error}. <Anchor component={Link} to="/">Back to projects</Anchor>
      </Alert>
    )
  }
  if (!project) return <PageLoader />

  if (project.status !== 'approved') {
    return (
      <Alert color={project.status === 'pending' ? 'yellow' : 'red'} title={project.name}>
        {project.status === 'pending'
          ? 'This project is waiting for an admin to approve it.'
          : `This project request was rejected${project.review_note ? `: ${project.review_note}` : '.'}`}{' '}
        <Anchor component={Link} to="/">
          Back to projects
        </Anchor>
      </Alert>
    )
  }

  const currentTab = location.pathname.split('/').pop()

  return (
    <Stack gap="md">
      <Breadcrumbs>
        <Anchor component={Link} to="/">
          Projects
        </Anchor>
        <Text>{project.name}</Text>
      </Breadcrumbs>

      <Group gap="sm">
        <Title order={2}>{project.name}</Title>
        <Badge variant="light" size="lg">
          {project.key}
        </Badge>
      </Group>

      <Tabs value={currentTab} onChange={(tab) => tab && navigate(tab)}>
        <Tabs.List>
          {TABS.map((tab) => (
            <Tabs.Tab key={tab.value} value={tab.value}>
              {tab.label}
            </Tabs.Tab>
          ))}
        </Tabs.List>
      </Tabs>

      <Outlet context={{ project } satisfies ProjectOutletContext} />
    </Stack>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useCurrentProject(): Project {
  return useOutletContext<ProjectOutletContext>().project
}
