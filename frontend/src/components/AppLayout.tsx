import { Anchor, AppShell, Badge, Button, Container, Group, Text } from '@mantine/core'
import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { usePendingCounts } from '../hooks/usePendingCounts'

export function AppLayout() {
  const { user, logout } = useAuth()
  const isAdmin = user?.role === 'admin'
  const pending = usePendingCounts(isAdmin)

  return (
    <AppShell header={{ height: 60 }} padding="md">
      <AppShell.Header>
        <Container size="xl" h="100%">
          <Group h="100%" justify="space-between" wrap="nowrap">
            <Group gap="lg" wrap="nowrap">
              <Anchor component={Link} to="/" fw={700} size="lg" underline="never">
                SprintBoard
              </Anchor>
              <Anchor component={NavLink} to="/" end size="sm" c="dimmed">
                Projects
              </Anchor>
              {isAdmin && (
                <Anchor component={NavLink} to="/admin/requests" size="sm" c="dimmed">
                  <Group gap={4} wrap="nowrap">
                    Requests
                    {pending.projects > 0 && (
                      <Badge size="xs" color="yellow" circle>
                        {pending.projects}
                      </Badge>
                    )}
                  </Group>
                </Anchor>
              )}
              {isAdmin && (
                <Anchor component={NavLink} to="/admin/users" size="sm" c="dimmed">
                  <Group gap={4} wrap="nowrap">
                    Users
                    {pending.users > 0 && (
                      <Badge size="xs" color="yellow" circle>
                        {pending.users}
                      </Badge>
                    )}
                  </Group>
                </Anchor>
              )}
            </Group>
            <Group gap="sm" wrap="nowrap">
              <Text size="sm" c="dimmed" visibleFrom="sm">
                Signed in as <strong>{user?.username}</strong>
              </Text>
              {isAdmin && (
                <Badge color="grape" variant="light">
                  Admin
                </Badge>
              )}
              <Button variant="default" size="xs" onClick={logout}>
                Log out
              </Button>
            </Group>
          </Group>
        </Container>
      </AppShell.Header>

      <AppShell.Main>
        <Container size="xl" px={0}>
          <Outlet />
        </Container>
      </AppShell.Main>
    </AppShell>
  )
}
