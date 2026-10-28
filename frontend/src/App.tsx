import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/AppLayout'
import { ProjectLayout } from './components/ProjectLayout'
import { AdminRoute, GuestRoute, ProtectedRoute } from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import { AdminRequestsPage } from './pages/AdminRequestsPage'
import { AdminUsersPage } from './pages/AdminUsersPage'
import { BacklogPage } from './pages/BacklogPage'
import { BoardPage } from './pages/BoardPage'
import { LoginPage } from './pages/LoginPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { ProjectsPage } from './pages/ProjectsPage'
import { RegisterPage } from './pages/RegisterPage'
import { SprintsPage } from './pages/SprintsPage'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<GuestRoute />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>

          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route index element={<ProjectsPage />} />
              <Route path="projects/:projectId" element={<ProjectLayout />}>
                <Route index element={<Navigate to="backlog" replace />} />
                <Route path="backlog" element={<BacklogPage />} />
                <Route path="sprints" element={<SprintsPage />} />
                <Route path="board" element={<BoardPage />} />
              </Route>
              <Route element={<AdminRoute />}>
                <Route path="admin/requests" element={<AdminRequestsPage />} />
                <Route path="admin/users" element={<AdminUsersPage />} />
              </Route>
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
