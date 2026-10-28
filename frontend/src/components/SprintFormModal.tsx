import { Button, Group, Modal, Stack, TextInput, Textarea } from '@mantine/core'
import { useForm } from '@mantine/form'
import { useState } from 'react'
import { sprintsApi } from '../api/sprints'
import { isoDate } from '../utils/constants'
import { notifyError, notifySuccess } from '../utils/notify'
import { lengthBetween, maxLength, required } from '../utils/validation'

interface SprintFormModalProps {
  opened: boolean
  projectId: number
  suggestedName: string
  onClose: () => void
  onSaved: () => void
}

export function SprintFormModal({ opened, onClose, ...props }: SprintFormModalProps) {
  return (
    <Modal opened={opened} onClose={onClose} title="New sprint">
      {opened && <SprintForm onClose={onClose} {...props} />}
    </Modal>
  )
}

function SprintForm({ projectId, suggestedName, onClose, onSaved }: Omit<SprintFormModalProps, 'opened'>) {
  const [saving, setSaving] = useState(false)
  const form = useForm({
    initialValues: {
      name: suggestedName,
      goal: '',
      start_date: isoDate(),
      end_date: isoDate(13),
    },
    validate: {
      name: lengthBetween('Name', 3, 60),
      goal: maxLength('Goal', 300),
      start_date: required('Start date'),
      end_date: (value, values) =>
        required('End date')(value) ??
        (value <= values.start_date ? 'End date must be after the start date' : null),
    },
  })

  async function handleSubmit(values: typeof form.values) {
    setSaving(true)
    try {
      await sprintsApi.create(projectId, {
        ...values,
        name: values.name.trim(),
        goal: values.goal.trim() || null,
      })
      notifySuccess(`${values.name.trim()} created`)
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
        <TextInput label="Name" withAsterisk data-autofocus {...form.getInputProps('name')} />
        <Textarea
          label="Sprint goal"
          placeholder="What should this sprint achieve?"
          autosize
          minRows={2}
          {...form.getInputProps('goal')}
        />
        <Group grow align="flex-start">
          <TextInput type="date" label="Start date" withAsterisk {...form.getInputProps('start_date')} />
          <TextInput type="date" label="End date" withAsterisk {...form.getInputProps('end_date')} />
        </Group>
        <Group justify="flex-end">
          <Button variant="default" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            Create sprint
          </Button>
        </Group>
      </Stack>
    </form>
  )
}
