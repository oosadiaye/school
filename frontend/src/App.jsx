import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './components/toast/ToastContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
import Courses from './pages/Courses';
import Results from './pages/Results';
import Academic from './pages/Academic';
import Finance from './pages/Finance';
import Library from './pages/Library';
import Hostel from './pages/Hostel';
import HR from './pages/HR';
import NUC from './pages/NUC';
import Faculties from './pages/Faculties';
import Departments from './pages/Departments';
import Programmes from './pages/Programmes';
import Users from './pages/Users';
import Settings from './pages/Settings';
import Layout from './components/Layout';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div style={{ background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#1e40af', fontSize: '1.5rem' }}>Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Layout><Dashboard /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/students" element={
        <ProtectedRoute>
          <Layout><Students /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/students/new" element={
        <ProtectedRoute>
          <Layout><Students /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/courses" element={
        <ProtectedRoute>
          <Layout><Courses /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/results" element={
        <ProtectedRoute>
          <Layout><Results /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/academic" element={
        <ProtectedRoute>
          <Layout><Academic /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/finance" element={
        <ProtectedRoute>
          <Layout><Finance /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/library" element={
        <ProtectedRoute>
          <Layout><Library /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/hostel" element={
        <ProtectedRoute>
          <Layout><Hostel /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/hr" element={
        <ProtectedRoute>
          <Layout><HR /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/nuc" element={
        <ProtectedRoute>
          <Layout><NUC /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/faculties" element={
        <ProtectedRoute>
          <Layout><Faculties /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/departments" element={
        <ProtectedRoute>
          <Layout><Departments /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/programmes" element={
        <ProtectedRoute>
          <Layout><Programmes /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/users" element={
        <ProtectedRoute>
          <Layout><Users /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/settings" element={
        <ProtectedRoute>
          <Layout><Settings /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Router>
          <AppRoutes />
        </Router>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
