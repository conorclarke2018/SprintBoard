import { notifications } from '@mantine/notifications'
import { ApiError } from '../api/client'

export function notifySuccess(message: string) {
  notifications.show({ color: 'green', message })
}

export function notifyError(error: unknown) {
  const message =
    error instanceof ApiError ? error.message : 'Something went wrong. Please try again.'
  notifications.show({ color: 'red', title: 'Error', message })
}
