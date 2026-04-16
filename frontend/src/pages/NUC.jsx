import { useState } from 'react';

const NUC = () => {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    programme: '',
    accreditation_status: 'pending',
    visit_date: '',
    expiry_date: '',
    remarks: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    alert('Accreditation record added!');
    setShowForm(false);
    setFormData({ programme: '', accreditation_status: 'pending', visit_date: '', expiry_date: '', remarks: '' });
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="students-page">
      <div className="page-header">
        <h1>NUC Compliance</h1>
        <button className="login-button" style={{ width: 'auto', marginTop: 0 }} onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Accreditation'}
        </button>
      </div>

      <div className="glass-stats-grid" style={{ marginBottom: '2.5rem' }}>
        <div className="glass-stat-card">
          <div className="glass-stat-icon" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>📚</div>
          <div className="glass-stat-info">
            <h3>12</h3>
            <p>Programmes</p>
          </div>
        </div>
        <div className="glass-stat-card">
          <div className="glass-stat-icon" style={{ background: 'rgba(34, 197, 94, 0.15)', color: '#4ade80' }}>✅</div>
          <div className="glass-stat-info">
            <h3>10</h3>
            <p>Accredited</p>
          </div>
        </div>
        <div className="glass-stat-card">
          <div className="glass-stat-icon" style={{ background: 'rgba(234, 179, 8, 0.15)', color: '#facc15' }}>⏳</div>
          <div className="glass-stat-info">
            <h3>2</h3>
            <p>Pending</p>
          </div>
        </div>
        <div className="glass-stat-card">
          <div className="glass-stat-icon" style={{ background: 'rgba(139, 92, 246, 0.15)', color: '#a78bfa' }}>📊</div>
          <div className="glass-stat-info">
            <h3>85%</h3>
            <p>Compliance</p>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="glass-card form-section">
          <h2>Add Accreditation Record</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="glass-label">Programme</label>
                <input className="glass-input" type="text" name="programme" value={formData.programme} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Status</label>
                <select className="glass-select" name="accreditation_status" value={formData.accreditation_status} onChange={handleChange}>
                  <option value="pending">Pending</option>
                  <option value="accredited">Accredited</option>
                  <option value="probation">Probation</option>
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Visit Date</label>
                <input className="glass-input" type="date" name="visit_date" value={formData.visit_date} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Expiry Date</label>
                <input className="glass-input" type="date" name="expiry_date" value={formData.expiry_date} onChange={handleChange} />
              </div>
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label className="glass-label">Remarks</label>
                <textarea className="glass-input" name="remarks" value={formData.remarks} onChange={handleChange} rows="2" />
              </div>
            </div>
            <button type="submit" className="login-button" style={{ width: 'auto', minWidth: '200px' }}>Save Record</button>
          </form>
        </div>
      )}

      <div className="glass-card table-section">
        <div style={{ overflowX: 'auto' }}>
          <table className="glass-table">
            <thead>
              <tr>
                <th>Programme</th>
                <th>Status</th>
                <th>Visit Date</th>
                <th>Expiry Date</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: '600', color: '#fff' }}>Computer Science</td>
                <td><span className="status-badge status-active">Accredited</span></td>
                <td>2024-01-15</td>
                <td>2029-01-14</td>
                <td>Full accreditation granted</td>
              </tr>
              <tr>
                <td style={{ fontWeight: '600', color: '#fff' }}>Electrical Engineering</td>
                <td><span className="status-badge status-active">Accredited</span></td>
                <td>2024-02-20</td>
                <td>2029-02-19</td>
                <td>Full accreditation granted</td>
              </tr>
              <tr>
                <td style={{ fontWeight: '600', color: '#fff' }}>Business Administration</td>
                <td><span className="status-badge status-pending">Pending</span></td>
                <td>2025-03-10</td>
                <td>-</td>
                <td>Awaiting inspection</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="no-data" style={{ marginTop: '1.5rem', opacity: 0.6 }}>NUC module ready. Connect to backend API for full functionality.</p>
      </div>
    </div>
  );
};

export default NUC;
