import { Badge, Paper, Stack, Table, Text, Title } from '@mantine/core'
import { useEffect, useState } from 'react'
import { authApi } from '../api/auth'
import { PageLoader } from '../components/PageLoader'
import type { User } from '../types'
import { notifyError } from '../utils/notify'

/** Read-only list of everyone with an approved account, so regular users can explore the users table. */
export function PeoplePage() {
  const [people, setPeople] = useState<User[] | null>(null)

  useEffect(() => {
    authApi
      .listUsers()
      .then(setPeople)
      .catch((error) => {
        notifyError(error)
        setPeople([])
      })
  }, [])

  if (people === null) return <PageLoader />

  return (
    <Stack>
      <Title order={2}>People</Title>
      <Text size="sm" c="dimmed">
        Everyone who can be assigned to an issue.
      </Text>
      <Paper withBorder>
        <Table verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Username</Table.Th>
              <Table.Th w={140}>Role</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {people.map((person) => (
              <Table.Tr key={person.id}>
                <Table.Td>{person.username}</Table.Td>
                <Table.Td>
                  <Badge color={person.role === 'admin' ? 'grape' : 'gray'} variant="light">
                    {person.role === 'admin' ? 'Admin' : 'User'}
                  </Badge>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Paper>
    </Stack>
  )
}
