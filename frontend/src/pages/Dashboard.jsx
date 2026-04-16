import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { studentService, academicService, financeService, libraryService, hostelService, hrService } from '../services/api';

const Icons = {
  Users: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>
  ),
  BookOpen: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" /></svg>
  ),
  Briefcase: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="14" x="2" y="7" rx="2" ry="2" /><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" /></svg>
  ),
  Home: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" /></svg>
  ),
  Calendar: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2" /><line x1="16" x2="16" y1="2" y2="6" /><line x1="8" x2="8" y1="2" y2="6" /><line x1="3" x2="21" y1="10" y2="10" /></svg>
  ),
  TrendingUp: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17" /><polyline points="16 7 22 7 22 13" /></svg>
  ),
  Clock: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>
  ),
  DollarSign: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="1" x2="12" y2="23" /><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg>
  ),
  Activity: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17" /><polyline points="16 7 22 7 22 13" /></svg>
  ),
  Bell: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" /><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" /></svg>
  ),
  Plus: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" x2="12" y1="5" y2="19" /><line x1="5" x2="19" y1="12" y2="12" /></svg>
  )
};

const ProgressRing = ({ percentage, color = "#3b82f6" }) => {
  const radius = 22;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div style={{ position: 'relative', width: '52px', height: '52px' }}>
      <svg width="52" height="52" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="26" cy="26" r={radius} fill="none" stroke="rgba(59, 130, 246, 0.1)" strokeWidth="5" />
        <circle cx="26" cy="26" r={radius} fill="none" stroke={color} strokeWidth="5" strokeDasharray={circumference} style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.5s ease', strokeLinecap: 'round' }} />
      </svg>
      <span style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontSize: '0.7rem', fontWeight: '700', color: '#1e40af' }}>{percentage}%</span>
    </div>
  );
};

const MiniStat = ({ icon, value, label, color }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem', background: 'rgba(255,255,255,0.6)', borderRadius: '14px', border: '1px solid rgba(59, 130, 246, 0.1)' }}>
    <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: `${color}15`, color: color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{icon}</div>
    <div>
      <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#1e40af' }}>{value}</div>
      <div style={{ fontSize: '0.7rem', color: '#64748b' }}>{label}</div>
    </div>
  </div>
);

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({ students: 0, courses: 0, employees: 0, books: 0, hostels: 0, sessions: 0 });
  const [financeStats, setFinanceStats] = useState({ totalCollected: 0, totalPending: 0, collectionRate: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [studentsRes, coursesRes, employeesRes, booksRes, hostelsRes, sessionsRes, financeRes] = await Promise.all([
          studentService.getStudents({ page_size: 1 }),
          academicService.getCourses({ page_size: 1 }),
          hrService.getEmployees({ page_size: 1 }),
          libraryService.getBooks({ page_size: 1 }),
          hostelService.getHostels(),
          academicService.getSessions(),
          financeService.getFinanceDashboard().catch(() => ({ data: {} })),
        ]);

        setStats({
          students: studentsRes.data.count || 0,
          courses: coursesRes.data.count || 0,
          employees: employeesRes.data.count || 0,
          books: booksRes.data.count || 0,
          hostels: hostelsRes.data.length || 0,
          sessions: sessionsRes.data.count || sessionsRes.data.length || 0,
        });

        if (financeRes.data) {
          setFinanceStats({
            totalCollected: financeRes.data.total_collected || 0,
            totalPending: financeRes.data.total_pending || 0,
            collectionRate: financeRes.data.collection_rate || 0,
          });
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user, navigate]);

  const statCards = [
    { name: 'Students', icon: <Icons.Users />, count: stats.students, color: '#3b82f6' },
    { name: 'Courses', icon: <Icons.BookOpen />, count: stats.courses, color: '#8b5cf6' },
    { name: 'Employees', icon: <Icons.Briefcase />, count: stats.employees, color: '#ef4444' },
    { name: 'Books', icon: <Icons.BookOpen />, count: stats.books, color: '#f59e0b' },
  ];

  const courses = [
    { name: 'Computer Science 101', progress: 85, color: '#3b82f6' },
    { name: 'Data Structures', progress: 62, color: '#8b5cf6' },
    { name: 'Web Development', progress: 91, color: '#f59e0b' },
    { name: 'Database Systems', progress: 74, color: '#10b981' },
  ];

  const events = [
    { title: 'Faculty Meeting', time: 'Today, 2:00 PM', color: '#3b82f6', icon: '📅' },
    { title: 'Midterm Exams', time: 'Next Week', color: '#8b5cf6', icon: '📝' },
    { title: 'Academic Seminar', time: 'March 15', color: '#f59e0b', icon: '🎓' },
  ];

  const activities = [
    { name: 'John Smith', action: 'submitted Assignment 3', time: '2 min ago', color: '#3b82f6' },
    { name: 'Emily Davis', action: 'enrolled in History 202', time: '1 hour ago', color: '#8b5cf6' },
    { name: 'Admin', action: 'announced Campus WiFi Maintenance', time: '3 hours ago', color: '#ef4444' },
    { name: 'Brian King', action: 'updated 5 student records', time: '5 hours ago', color: '#10b981' },
  ];

  return (
    <div className="dashboard-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2 className="page-title" style={{ margin: 0 }}>Dashboard</h2>
        <button style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', color: 'white', border: 'none', borderRadius: '10px', padding: '0.7rem 1.2rem', fontWeight: '600', fontSize: '0.85rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)' }}>
          <Icons.Plus /> Add Events
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        {statCards.map((item) => (
          <div key={item.name} style={{ background: 'rgba(255, 255, 255, 0.7)', backdropFilter: 'blur(20px)', border: '1px solid rgba(59, 130, 246, 0.15)', borderRadius: '16px', padding: '1.25rem', display: 'flex', alignItems: 'center', gap: '1rem', transition: 'all 0.3s ease', cursor: 'pointer' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: `${item.color}15`, color: item.color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{item.icon}</div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: '800', color: '#1e40af' }}>{loading ? '...' : item.count.toLocaleString()}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: '500' }}>{item.name}</div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div style={{ background: 'rgba(255, 255, 255, 0.7)', backdropFilter: 'blur(30px)', border: '1px solid rgba(59, 130, 246, 0.15)', borderRadius: '20px', padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#1e40af', fontWeight: '700', textShadow: '1px 1px 0 rgba(59, 130, 246, 0.2)' }}>Course Progress</h3>
            <Icons.TrendingUp style={{ color: '#64748b' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {courses.map((course, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.75rem', background: 'rgba(59, 130, 246, 0.05)', borderRadius: '12px' }}>
                <ProgressRing percentage={course.progress} color={course.color} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#1e40af' }}>{course.name}</div>
                  <div style={{ height: '6px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '3px', marginTop: '0.5rem', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${course.progress}%`, background: `linear-gradient(90deg, ${course.color}, ${course.color}80)`, borderRadius: '3px' }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.7)', backdropFilter: 'blur(30px)', border: '1px solid rgba(59, 130, 246, 0.15)', borderRadius: '20px', padding: '1.5rem', flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#1e40af', fontWeight: '700', textShadow: '1px 1px 0 rgba(59, 130, 246, 0.2)' }}>Upcoming Events</h3>
              <Icons.Calendar style={{ color: '#64748b' }} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {events.map((event, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', background: 'rgba(59, 130, 246, 0.05)', borderRadius: '12px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: `${event.color}15`, color: event.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem' }}>{event.icon}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: '600', color: '#1e40af' }}>{event.title}</div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Icons.Clock /> {event.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ background: 'rgba(255, 255, 255, 0.7)', backdropFilter: 'blur(30px)', border: '1px solid rgba(59, 130, 246, 0.15)', borderRadius: '20px', padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#1e40af', fontWeight: '700', textShadow: '1px 1px 0 rgba(59, 130, 246, 0.2)' }}>Finance Overview</h3>
              <Icons.DollarSign style={{ color: '#64748b' }} />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <MiniStat icon={<Icons.DollarSign />} value={`₦${(financeStats.totalCollected / 1000000).toFixed(1)}M`} label="Collected" color="#10b981" />
              <MiniStat icon={<Icons.Activity />} value={`₦${(financeStats.totalPending / 1000000).toFixed(1)}M`} label="Pending" color="#f59e0b" />
            </div>
          </div>
        </div>

        <div style={{ gridColumn: '1 / -1', background: 'rgba(255, 255, 255, 0.7)', backdropFilter: 'blur(30px)', border: '1px solid rgba(59, 130, 246, 0.15)', borderRadius: '20px', padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#1e40af', fontWeight: '700', textShadow: '1px 1px 0 rgba(59, 130, 246, 0.2)' }}>Recent Activity</h3>
            <Icons.Activity style={{ color: '#64748b' }} />
          </div>
          <div style={{ display: 'flex', gap: '1.5rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
            {activities.map((activity, idx) => (
              <div key={idx} style={{ minWidth: '220px', padding: '1rem', background: 'rgba(59, 130, 246, 0.05)', borderRadius: '14px', border: '1px solid rgba(59, 130, 246, 0.1)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                  <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: activity.color, color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', fontWeight: '700' }}>{activity.name.split(' ').map(n => n[0]).join('')}</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: '600', color: '#1e40af' }}>{activity.name}</div>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#475569', marginBottom: '0.25rem' }}>{activity.action}</div>
                <div style={{ fontSize: '0.7rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Icons.Clock /> {activity.time}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
