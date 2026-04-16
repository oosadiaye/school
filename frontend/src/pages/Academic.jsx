import { useState, useEffect } from 'react';
import { academicService } from '../services/api';

const Academic = () => {
  const [sessions, setSessions] = useState([]);
  const [semesters, setSemesters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('sessions');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '', start_date: '', end_date: '', is_current: false, is_registration_open: false
  });

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [sessRes, semRes] = await Promise.all([
        academicService.getSessions(), academicService.getSemesters()
      ]);
      setSessions(sessRes.data.results || sessRes.data);
      setSemesters(semRes.data.results || semRes.data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await academicService.createSession(formData);
      setShowForm(false);
      fetchData();
    } catch (error) {
      alert('Error creating session');
    }
  };

  return (
    <div className="students-page">
      <div className="page-header">
        <h1 style={{ color: '#1e40af', fontWeight: 800, letterSpacing: '-0.03em', margin: 0, WebkitTextStroke: '1px rgba(59, 130, 246, 0.5)', textShadow: '2px 2px 0 rgba(59, 130, 246, 0.3), -1px -1px 0 rgba(59, 130, 246, 0.2), 1px -1px 0 rgba(59, 130, 246, 0.2), -1px 1px 0 rgba(59, 130, 246, 0.2)' }}>Academic Calendar</h1>
      </div>

      <div className="glass-tabs">
        <button className={`glass-tab ${activeTab === 'sessions' ? 'active' : ''}`} onClick={() => setActiveTab('sessions')}>Sessions</button>
        <button className={`glass-tab ${activeTab === 'semesters' ? 'active' : ''}`} onClick={() => setActiveTab('semesters')}>Semesters</button>
      </div>

      {activeTab === 'sessions' && (
        <div className="tab-content">
          <div className="page-header" style={{ marginBottom: '1.5rem', marginTop: 0 }}>
            <h2 style={{ color: '#1e40af', fontSize: '1.5rem', fontWeight: 700, textShadow: '1px 1px 0 rgba(59, 130, 246, 0.2)' }}>Academic Sessions</h2>
            <button className="login-button" style={{ width: 'auto', marginTop: 0 }} onClick={() => setShowForm(!showForm)}>
              {showForm ? 'Cancel' : 'Add Session'}
            </button>
          </div>

          {showForm && (
            <div className="glass-card form-section">
              <form onSubmit={handleSubmit}>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="glass-label">Session Name</label>
                    <input className="glass-input" type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="2024/2025" required />
                  </div>
                  <div className="form-group">
                    <label className="glass-label">Start Date</label>
                    <input className="glass-input" type="date" value={formData.start_date} onChange={(e) => setFormData({ ...formData, start_date: e.target.value })} required />
                  </div>
                  <div className="form-group">
                    <label className="glass-label">End Date</label>
                    <input className="glass-input" type="date" value={formData.end_date} onChange={(e) => setFormData({ ...formData, end_date: e.target.value })} required />
                  </div>
                </div>
                <button type="submit" className="login-button" style={{ width: 'auto', minWidth: '180px', marginTop: '1.5rem' }}>Create</button>
              </form>
            </div>
          )}

          <div className="glass-card table-section">
            {loading ? (
              <p className="no-data">Loading...</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="glass-table">
                  <thead>
                    <tr>
                      <th>Session</th>
                      <th>Start</th>
                      <th>End</th>
                      <th>Current</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sessions.map(s => (
                      <tr key={s.id}>
                        <td style={{ fontWeight: '600', color: '#1e40af' }}>{s.name}</td>
                        <td>{s.start_date}</td>
                        <td>{s.end_date}</td>
                        <td>
                          <span className={`status-badge ${s.is_current ? 'status-active' : ''}`}>
                            {s.is_current ? 'Current' : 'Previous'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'semesters' && (
        <div className="tab-content">
          <div className="page-header" style={{ marginBottom: '1.5rem', marginTop: 0 }}>
            <h2 style={{ color: '#1e40af', fontSize: '1.5rem', fontWeight: 700, textShadow: '1px 1px 0 rgba(59, 130, 246, 0.2)' }}>Semesters</h2>
          </div>
          <div className="glass-card table-section">
            {loading ? (
              <p className="no-data">Loading...</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="glass-table">
                  <thead>
                    <tr>
                      <th>Semester</th>
                      <th>Session</th>
                      <th>Start</th>
                      <th>End</th>
                      <th>Active</th>
                    </tr>
                  </thead>
                  <tbody>
                    {semesters.map(s => (
                      <tr key={s.id}>
                        <td style={{ fontWeight: '600', color: '#1e40af' }}>{s.name}</td>
                        <td>{s.session_name}</td>
                        <td>{s.start_date}</td>
                        <td>{s.end_date}</td>
                        <td>
                          <span className={`status-badge ${s.is_active ? 'status-active' : ''}`}>
                            {s.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Academic;
