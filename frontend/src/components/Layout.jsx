import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { studentService, academicService } from '../services/api';
import './Layout.css';

// Custom SVG Icons for Sidebar
const Icons = {
  Dashboard: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /></svg>,
  Users: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>,
  Book: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" /></svg>,
  Edit: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" /><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" /></svg>,
  Calendar: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg>,
  Dollar: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="1" x2="12" y2="23" /><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg>,
  Library: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m16 6 4 14" /><path d="M12 6v14" /><path d="M8 8v12" /><path d="M4 4v16" /><path d="M2 20h20" /></svg>,
  Home: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" /></svg>,
  Briefcase: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2" /><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" /></svg>,
  Academy: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z" /><path d="M6 12v5c3 3 9 3 12 0v-5" /></svg>,
  Building: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2" /><line x1="9" y1="22" x2="9" y2="22" /><line x1="15" y1="22" x2="15" y2="22" /><line x1="12" y1="18" x2="12" y2="18" /><line x1="12" y1="14" x2="12" y2="14" /><line x1="12" y1="10" x2="12" y2="10" /><line x1="12" y1="6" x2="12" y2="6" /><line x1="8" y1="18" x2="8" y2="18" /><line x1="8" y1="14" x2="8" y2="14" /><line x1="8" y1="10" x2="8" y2="10" /><line x1="8" y1="6" x2="8" y2="6" /><line x1="16" y1="18" x2="16" y2="18" /><line x1="16" y1="14" x2="16" y2="14" /><line x1="16" y1="10" x2="16" y2="10" /><line x1="16" y1="6" x2="16" y2="6" /></svg>,
  Settings: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" /></svg>,
  Bell: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" /><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" /></svg>,
  Search: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
};

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [stats, setStats] = useState({ students: 0, courses: 0 });
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    const fetchStats = async () => {
      try {
        const [studentsRes, coursesRes] = await Promise.all([
          studentService.getStudents({ page_size: 1 }),
          academicService.getCourses({ page_size: 1 }),
        ]);
        setStats({
          students: studentsRes.data.count || 0,
          courses: coursesRes.data.count || 0,
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    fetchStats();
  }, [user, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { name: 'Dashboard', icon: <Icons.Dashboard />, path: '/dashboard' },
    { name: 'Students', icon: <Icons.Users />, path: '/students', count: stats.students },
    { name: 'Courses', icon: <Icons.Book />, path: '/courses', count: stats.courses },
    { name: 'Results', icon: <Icons.Edit />, path: '/results' },
    { name: 'Academic', icon: <Icons.Calendar />, path: '/academic' },
    { name: 'Finance', icon: <Icons.Dollar />, path: '/finance' },
    { name: 'Library', icon: <Icons.Library />, path: '/library' },
    { name: 'Hostel', icon: <Icons.Home />, path: '/hostel' },
    { name: 'HR', icon: <Icons.Briefcase />, path: '/hr' },
    { name: 'NUC', icon: <Icons.Academy />, path: '/nuc' },
    { name: 'Faculties', icon: <Icons.Building />, path: '/faculties' },
    { name: 'Departments', icon: <Icons.Building />, path: '/departments' },
    { name: 'Programmes', icon: <Icons.Academy />, path: '/programmes' },
    { name: 'Users', icon: <Icons.Settings />, path: '/users' },
    { name: 'Settings', icon: <Icons.Settings />, path: '/settings' },
  ];

  return (
    <div className="app-layout">
      <button className="menu-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
        {sidebarOpen ? '✕' : '☰'}
      </button>

      <aside className={`glass-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2 style={{ letterSpacing: '2px', fontWeight: '900' }}>TIMS</h2>
          <p>University System</p>
        </div>
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <a
              key={item.name}
              href={item.path}
              className={`glass-nav-item ${location.pathname === item.path ? 'active' : ''}`}
              onClick={(e) => {
                e.preventDefault();
                navigate(item.path);
                setSidebarOpen(false);
              }}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.name}</span>
              {item.count > 0 && <span className="nav-count">{item.count}</span>}
            </a>
          ))}
        </nav>
        <div className="sidebar-footer">
          <button onClick={handleLogout} className="glass-logout-btn">
            Logout
          </button>
        </div>
      </aside>

      {sidebarOpen && <div className="glass-overlay" onClick={() => setSidebarOpen(false)}></div>}

      <main className="glass-main">
        <header className="glass-header">
          <div className="header-search">
            <span className="search-icon" style={{ color: '#64748b' }}><Icons.Search /></span>
            <input type="text" placeholder="Search..." className="glass-input" style={{ width: '300px', border: 'none', background: 'rgba(255, 255, 255, 0.6)', color: '#1e40af' }} />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div className="notification-bell" style={{ position: 'relative', cursor: 'pointer', opacity: 0.6, color: '#1e40af' }}>
              <Icons.Bell />
              <span style={{ position: 'absolute', top: '-5px', right: '-5px', width: '8px', height: '8px', background: '#ef4444', borderRadius: '50%' }}></span>
            </div>

            <div className="user-badge" style={{ padding: '0.4rem 0.8rem', borderRadius: '12px' }}>
              <div className="avatar" style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: '600', color: 'white' }}>
                {user?.first_name?.[0] || user?.username?.[0] || 'U'}
              </div>
              <span style={{ fontSize: '0.85rem', color: '#1e40af' }}>
                {user?.first_name || user?.username}
              </span>
            </div>
          </div>
        </header>
        <div className="glass-content">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
