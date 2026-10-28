import { Badge, Button, Group, Select, Stack, Table, Text, Title } from '@mantine/core'
import { useCallback, useEffect, useState } from 'react'
import { adminApi } from '../api/admin'
import { ConfirmModal } from '../components/ConfirmModal'
import { PageLoader } from '../components/PageLoader'
import { useAuth } from '../context/AuthContext'
import { REQUESTS_CHANGED_EVENT } from '../hooks/usePendingCounts'
import type { AdminUser, UserRole } from '../types'
import { formatDate } from '../utils/constants'
import { notifyError, notifySuccess } from '../utils/notify'

const ROLE_OPTIONS = [
  { value: 'user', label: 'User' },
  { value: 'admin', label: 'Admin' },
]

export function AdminUsersPage() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<AdminUser[] | null>(null)
  const [deleting, setDeleting] = useState<AdminUser | null>(null)

  const loadUsers = useCallback(() => {
    adminApi
      .listUsers()
      .then(setUsers)
      .catch((error) => {
        notifyError(error)
        setUsers([])
      })
  }, [])

  useEffect(loadUsers, [loadUsers])

  function refreshAll() {
    loadUsers()
    window.dispatchEvent(new Event(REQUESTS_CHANGED_EVENT))
  }

  async function approveUser(user: AdminUser) {
    try {
      await adminApi.approveUser(user.id)
      notifySuccess(`${user.username} can now log in`)
      refreshAll()
    } catch (error) {
      notifyError(error)
    }
  }

  async function changeRole(user: AdminUser, role: UserRole) {
    try {
      await adminApi.setRole(user.id, role)
      notifySuccess(`${user.username} is now ${role === 'admin' ? 'an admin' : 'a user'}`)
      loadUsers()
    } catch (error) {
      notifyError(error)
    }
  }

  async function deleteUser(user: AdminUser) {
    await adminApi.deleteUser(user.id)
    notifySuccess(user.is_approved ? `${user.username} deleted` : `${user.username}'s sign-up rejected`)
    refreshAll()
  }

  if (users === null) return <PageLoader />

  // Accounts waiting for approval are listed first.
  const sortedUsers = [...users].sort((a, b) => Number(a.is_approved) - Number(b.is_approved))

  return (
    <Stack>
      <div>
        <Title order={2}>Users</Title>
        <Text c="dimmed" size="sm">
          New sign-ups cannot log in until an admin approves them. Admins can see and manage every
          project and every account.
        </Text>
      </div>

      <Table.ScrollContainer minWidth={600}>
        <Table verticalSpacing="sm" highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Username</Table.Th>
              <Table.Th w={140}>Role</Table.Th>
              <Table.Th w={100}>Projects</Table.Th>
              <Table.Th w={140}>Joined</Table.Th>
              <Table.Th w={170} />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {sortedUsers.map((user) => {
              const isMe = user.id === currentUser?.id
              return (
                <Table.Tr key={user.id}>
                  <Table.Td>
                    <Group gap="xs">
                      <Text fw={500}>{user.username}</Text>
                      {isMe && <Badge variant="light">You</Badge>}
                      {!user.is_approved && (
                        <Badge color="yellow" variant="light">
                          Awaiting approval
                        </Badge>
                      )}
                    </Group>
                  </Table.Td>
                  <Table.Td>
                    <Select
                      size="xs"
                      aria-label={`Role for ${user.username}`}
                      data={ROLE_OPTIONS}
                      value={user.role}
                      allowDeselect={false}
                      disabled={isMe}
                      title={isMe ? 'You cannot change your own role' : undefined}
                      onChange={(value) => value && value !== user.role && changeRole(user, value as UserRole)}
                    />
                  </Table.Td>
                  <Table.Td>{user.project_count}</Table.Td>
                  <Table.Td>{formatDate(user.created_at.slice(0, 10))}</Table.Td>
                  <Table.Td>
                    <Group gap={4} justify="flex-end" wrap="nowrap">
                      {!user.is_approved && (
                        <Button size="compact-xs" color="green" onClick={() => approveUser(user)}>
                          Approve
                        </Button>
                      )}
                      {!isMe && (
                        <Button size="compact-xs" variant="subtle" color="red" onClick={() => setDeleting(user)}>
                          {user.is_approved ? 'Delete' : 'Reject'}
                        </Button>
                      )}
                    </Group>
                  </Table.Td>
                </Table.Tr>
              )
            })}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>

      <ConfirmModal
        opened={deleting !== null}
        title={deleting?.is_approved === false ? `Reject ${deleting.username}?` : `Delete ${deleting?.username ?? 'user'}?`}
        message={
          deleting?.is_approved === false
            ? 'The sign-up is removed. They can register again later if needed.'
            : `This deletes the account and its ${deleting?.project_count ?? 0} project(s). Issues assigned to this user become unassigned.`
        }
        confirmLabel={deleting?.is_approved === false ? 'Reject sign-up' : 'Delete user'}
        onConfirm={() => deleteUser(deleting!)}
        onClose={() => setDeleting(null)}
      />
    </Stack>
  )
}
