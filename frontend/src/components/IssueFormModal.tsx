import { Button, Group, Modal, Select, Stack, TextInput, Textarea } from '@mantine/core'
import { useForm } from '@mantine/form'
import { useState } from 'react'
import { issuesApi } from '../api/issues'
import type { Issue, IssuePriority, IssueStatus, IssueType, Sprint, User } from '../types'
import { PRIORITY_OPTIONS, STATUS_OPTIONS, STORY_POINT_OPTIONS, TYPE_OPTIONS } from '../utils/constants'
import { notifyError, notifySuccess } from '../utils/notify'
import { lengthBetween, maxLength } from '../utils/validation'

interface IssueFormModalProps {
  opened: boolean
  projectId: number
  issue: Issue | null
  sprints: Sprint[]
  users: User[]
  onClose: () => void
  onSaved: () => void
}

export function IssueFormModal({ opened, onClose, issue, ...props }: IssueFormModalProps) {
  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={issue ? `Edit ${issue.key}` : 'Create issue'}
      size="lg"
    >
      {opened && <IssueForm issue={issue} onClose={onClose} {...props} />}
    </Modal>
  )
}

const toId = (value: string | null) => (value ? Number(value) : null)
const fromId = (value: number | null | undefined) => (value == null ? null : String(value))

function IssueForm({ projectId, issue, sprints, users, onClose, onSaved }: Omit<IssueFormModalProps, 'opened'>) {
  const [saving, setSaving] = useState(false)
  const form = useForm({
    initialValues: {
      title: issue?.title ?? '',
      description: issue?.description ?? '',
      type: (issue?.type ?? 'story') as IssueType,
      priority: (issue?.priority ?? 'medium') as IssuePriority,
      status: (issue?.status ?? 'todo') as IssueStatus,
      story_points: fromId(issue?.story_points),
      assignee_id: fromId(issue?.assignee?.id),
      sprint_id: fromId(issue?.sprint_id),
    },
    validate: {
      title: lengthBetween('Title', 3, 120),
      description: maxLength('Description', 2000),
    },
  })

  const sprintOptions = sprints
    .filter((sprint) => sprint.status !== 'completed' || sprint.id === issue?.sprint_id)
    .map((sprint) => ({ value: String(sprint.id), label: sprint.name }))
  const userOptions = users.map((user) => ({ value: String(user.id), label: user.username }))

  async function handleSubmit(values: typeof form.values) {
    setSaving(true)
    const input = {
      title: values.title.trim(),
      description: values.description.trim() || null,
      type: values.type,
      priority: values.priority,
      story_points: toId(values.story_points),
      assignee_id: toId(values.assignee_id),
      sprint_id: toId(values.sprint_id),
    }
    try {
      if (issue) {
        await issuesApi.update(issue.id, { ...input, status: values.status })
        notifySuccess(`${issue.key} updated`)
      } else {
        const created = await issuesApi.create(projectId, input)
        notifySuccess(`${created.key} created`)
      }
      onSaved()
      onClose()
    } catch (error) {
      notifyError(error)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={form.onSubmit(handleSubmit)} noValidate>
      <Stack>
        <TextInput
          label="Title"
          placeholder="What needs to be done?"
          withAsterisk
          data-autofocus
          {...form.getInputProps('title')}
        />
        <Textarea label="Description" autosize minRows={3} {...form.getInputProps('description')} />

        <Group grow align="flex-start">
          <Select label="Type" data={TYPE_OPTIONS} allowDeselect={false} {...form.getInputProps('type')} />
          <Select
            label="Priority"
            data={PRIORITY_OPTIONS}
            allowDeselect={false}
            {...form.getInputProps('priority')}
          />
          {issue && (
            <Select
              label="Status"
              data={STATUS_OPTIONS}
              allowDeselect={false}
              {...form.getInputProps('status')}
            />
          )}
        </Group>

        <Group grow align="flex-start">
          <Select
            label="Story points"
            placeholder="Not estimated"
            data={STORY_POINT_OPTIONS}
            clearable
            {...form.getInputProps('story_points')}
          />
          <Select
            label="Assignee"
            placeholder="Unassigned"
            data={userOptions}
            clearable
            searchable
            {...form.getInputProps('assignee_id')}
          />
        </Group>

        <Select
          label="Sprint"
          placeholder="Backlog (no sprint)"
          data={sprintOptions}
          clearable
          {...form.getInputProps('sprint_id')}
        />

        <Group justify="flex-end">
          <Button variant="default" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {issue ? 'Save changes' : 'Create issue'}
          </Button>
        </Group>
      </Stack>
    </form>
  )
}
