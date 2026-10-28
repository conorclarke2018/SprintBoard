import { Button, Group, Modal, Stack, Text, TextInput, Textarea } from '@mantine/core'
import { useForm } from '@mantine/form'
import { useState } from 'react'
import { projectsApi } from '../api/projects'
import { useAuth } from '../context/AuthContext'
import type { Project } from '../types'
import { notifyError, notifySuccess } from '../utils/notify'
import { lengthBetween, maxLength, validateProjectKey } from '../utils/validation'

interface ProjectFormModalProps {
  opened: boolean
  project: Project | null
  onClose: () => void
  onSaved: () => void
}

export function ProjectFormModal({ opened, project, onClose, onSaved }: ProjectFormModalProps) {
  const isAdmin = useAuth().user?.role === 'admin'
  const title = project ? 'Edit project' : isAdmin ? 'New project' : 'Request a new project'

  return (
    <Modal opened={opened} onClose={onClose} title={title}>
      {opened && <ProjectForm project={project} onClose={onClose} onSaved={onSaved} />}
    </Modal>
  )
}

function ProjectForm({ project, onClose, onSaved }: Omit<ProjectFormModalProps, 'opened'>) {
  const isAdmin = useAuth().user?.role === 'admin'
  const [saving, setSaving] = useState(false)
  const form = useForm({
    initialValues: {
      name: project?.name ?? '',
      key: project?.key ?? '',
      description: project?.description ?? '',
    },
    validate: {
      name: lengthBetween('Name', 3, 100),
      key: project ? undefined : validateProjectKey,
      description: maxLength('Description', 500),
    },
  })

  async function handleSubmit(values: typeof form.values) {
    setSaving(true)
    const input = { name: values.name.trim(), description: values.description.trim() || null }
    try {
      if (project) {
        const updated = await projectsApi.update(project.id, input)
        notifySuccess(
          project.status === 'rejected' && updated.status === 'pending'
            ? 'Changes saved and request sent to an admin again'
            : 'Project updated',
        )
      } else {
        const created = await projectsApi.create({ ...input, key: values.key.trim() })
        notifySuccess(
          created.status === 'approved'
            ? `Project ${created.key} created`
            : `Request for ${created.key} sent. An admin will review it soon.`,
        )
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
        {!project && !isAdmin && (
          <Text size="sm" c="dimmed">
            New projects need an admin's approval before you can add issues and sprints.
          </Text>
        )}
        {project?.status === 'rejected' && !isAdmin && (
          <Text size="sm" c="dimmed">
            Saving your changes will send this request to an admin again.
          </Text>
        )}
        <TextInput label="Name" placeholder="e.g. Company website" withAsterisk data-autofocus {...form.getInputProps('name')} />
        <TextInput
          label="Key"
          description={
            project ? 'The key cannot be changed' : '2 to 5 letters, used in issue ids such as SB-12'
          }
          placeholder="SB"
          withAsterisk
          disabled={Boolean(project)}
          {...form.getInputProps('key')}
          onChange={(event) => form.setFieldValue('key', event.currentTarget.value.toUpperCase())}
        />
        <Textarea label="Description" autosize minRows={2} {...form.getInputProps('description')} />
        <Group justify="flex-end">
          <Button variant="default" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {project ? 'Save changes' : isAdmin ? 'Create project' : 'Send request'}
          </Button>
        </Group>
      </Stack>
    </form>
  )
}
