import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Machines from './pages/Machines'
import MachineDetail from './pages/MachineDetail'
import Lignes from './pages/Lignes'
import LigneDetail from './pages/LigneDetail'
import Pannes from './pages/Pannes'
import Interventions from './pages/Interventions'
import Pieces from './pages/Pieces'
import Recherche from './pages/Recherche'
import Utilisateurs from './pages/Utilisateurs'
import Activite from './pages/Activite'
import PanneDetail from './pages/PanneDetail'
import RapportPanne from './pages/RapportPanne'
import MaintenancePreventive from './pages/MaintenancePreventive'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()
  if (isLoading) return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-orange-500" />
    </div>
  )
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()
  if (isLoading) return null
  if (!user) return <Navigate to="/login" replace />
  if (user.role !== 'admin') return <Navigate to="/" replace />
  return <>{children}</>
}

function AppRoutes() {
  const { user } = useAuth()
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="machines" element={<Machines />} />
        <Route path="machines/:id" element={<MachineDetail />} />
        <Route path="lignes" element={<Lignes />} />
        <Route path="lignes/:ligne" element={<LigneDetail />} />
        <Route path="pannes" element={<Pannes />} />
        <Route path="pannes/:id" element={<PanneDetail />} />
        <Route path="pannes/:id/rapport" element={<RapportPanne />} />
        <Route path="maintenance-preventive" element={<MaintenancePreventive />} />
        <Route path="interventions" element={<Interventions />} />
        <Route path="pieces" element={<Pieces />} />
        <Route path="recherche" element={<Recherche />} />
        <Route path="utilisateurs" element={<AdminRoute><Utilisateurs /></AdminRoute>} />
        <Route path="activite" element={<AdminRoute><Activite /></AdminRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
        <Toaster
          position="top-right"
          toastOptions={{
            style: { background: '#1f2937', color: '#f9fafb', border: '1px solid #374151' },
            success: { iconTheme: { primary: '#f97316', secondary: '#fff' } },
          }}
        />
      </BrowserRouter>
    </AuthProvider>
  )
}
