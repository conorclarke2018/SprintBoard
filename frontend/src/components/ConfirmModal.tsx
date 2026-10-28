import { Button, Group, Modal, Text } from '@mantine/core'
import { useState } from 'react'
import type { ReactNode } from 'react'
import { notifyError } from '../utils/notify'

interface ConfirmModalProps {
  opened: boolean
  title: string
  message: ReactNode
  confirmLabel: string
  color?: string
  onConfirm: () => Promise<void>
  onClose: () => void
}

export function ConfirmModal({
  opened,
  title,
  message,
  confirmLabel,
  color = 'red',
  onConfirm,
  onClose,
}: ConfirmModalProps) {
  const [busy, setBusy] = useState(false)

  async function handleConfirm() {
    setBusy(true)
    try {
      await onConfirm()
      onClose()
    } catch (error) {
      notifyError(error)
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal opened={opened} onClose={onClose} title={title} centered>
      <Text size="sm">{message}</Text>
      <Group justify="flex-end" mt="lg">
        <Button variant="default" onClick={onClose} disabled={busy}>
          Cancel
        </Button>
        <Button color={color} onClick={handleConfirm} loading={busy}>
          {confirmLabel}
        </Button>
      </Group>
    </Modal>
  )
}
