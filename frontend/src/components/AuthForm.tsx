import { Anchor, Button, Center, Paper, PasswordInput, Stack, Text, TextInput, Title } from '@mantine/core'
import { useForm } from '@mantine/form'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { notifyError, notifySuccess } from '../utils/notify'
import { required, validatePassword, validateUsername } from '../utils/validation'

interface AuthFormProps {
  mode: 'login' | 'register'
}

export function AuthForm({ mode }: AuthFormProps) {
  const isRegister = mode === 'register'
  const { login, register } = useAuth()
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)

  const form = useForm({
    initialValues: { username: '', password: '', confirmPassword: '' },
    validate: {
      username: isRegister ? validateUsername : required('Username'),
      password: isRegister ? validatePassword : required('Password'),
      confirmPassword: (value, values) =>
        isRegister && value !== values.password ? 'Passwords do not match' : null,
    },
  })

  async function handleSubmit(values: typeof form.values) {
    setSubmitting(true)
    const credentials = { username: values.username.trim(), password: values.password }
    try {
      if (isRegister) {
        const user = await register(credentials)
        if (user.is_approved) {
          notifySuccess('Account created. As the first user, you are the admin.')
        } else {
          notifySuccess('Account created. You can log in once an admin approves it.')
          form.reset()
          setSubmitting(false)
          navigate('/login')
        }
      } else {
        await login(credentials)
      }
    } catch (error) {
      notifyError(error)
      setSubmitting(false)
    }
  }

  return (
    <Center mih="100vh" p="md">
      <Paper withBorder shadow="sm" p="xl" radius="md" w="100%" maw={420}>
        <form onSubmit={form.onSubmit(handleSubmit)} noValidate>
          <Stack>
            <div>
              <Title order={2}>{isRegister ? 'Create an account' : 'Welcome back'}</Title>
              <Text c="dimmed" size="sm">
                {isRegister
                  ? 'Start planning sprints with SprintBoard'
                  : 'Log in to see your projects and boards'}
              </Text>
            </div> 

            <TextInput
              label="Username"
              autoComplete="username"
              description={isRegister ? 'Letters, numbers and underscores' : undefined}
              {...form.getInputProps('username')}
            />
            <PasswordInput
              label="Password"
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              description={isRegister ? 'At least 8 characters' : undefined}
              {...form.getInputProps('password')}
            />
            {isRegister && (
              <PasswordInput
                label="Confirm password"
                autoComplete="new-password"
                {...form.getInputProps('confirmPassword')}
              />
            )}

            <Button type="submit" loading={submitting} fullWidth>
              {isRegister ? 'Create account' : 'Log in'}
            </Button>

            <Text size="sm" ta="center">
              {isRegister ? 'Already have an account? ' : "Don't have an account? "}
              <Anchor component={Link} to={isRegister ? '/login' : '/register'}>
                {isRegister ? 'Log in' : 'Register'}
              </Anchor>
            </Text>
          </Stack>
        </form>
      </Paper>
    </Center>
  )
}
