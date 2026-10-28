import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { authApi } from '../api/auth'
import { LOGOUT_EVENT, tokenStorage } from '../api/client'
import type { Credentials, User } from '../types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (credentials: Credentials) => Promise<void>
  register: (credentials: Credentials) => Promise<User>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(() => tokenStorage.get() !== null)

  useEffect(() => {
    if (!tokenStorage.get()) return
    authApi
      .me()
      .then(setUser)
      .catch(() => tokenStorage.clear())
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    const handleLogout = () => setUser(null)
    window.addEventListener(LOGOUT_EVENT, handleLogout)
    return () => window.removeEventListener(LOGOUT_EVENT, handleLogout)
  }, [])

  const login = useCallback(async (credentials: Credentials) => {
    const token = await authApi.login(credentials)
    tokenStorage.set(token.access_token)
    setUser(token.user)
  }, [])

  const register = useCallback(
    async (credentials: Credentials) => {
      const user = await authApi.register(credentials)
      // Only the first account is approved straight away; others wait for an admin.
      if (user.is_approved) await login(credentials)
      return user
    },
    [login],
  )

  const logout = useCallback(() => {
    tokenStorage.clear()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}
