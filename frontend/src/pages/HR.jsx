import { useState } from 'react';

const HR = () => {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    department: '',
    position: '',
    employment_type: 'full_time',
    salary: '',
    start_date: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    alert('Staff added successfully!');
    setShowForm(false);
    setFormData({ first_name: '', last_name: '', email: '', phone: '', department: '', position: '', employment_type: 'full_time', salary: '', start_date: '' });
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const departments = ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Engineering'];

  return (
    <div className="students-page">
      <div className="page-header">
        <h1>Human Resources</h1>
        <button className="login-button" style={{ width: 'auto', marginTop: 0 }} onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Staff'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card form-section">
          <h2>Add New Staff</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="glass-label">First Name</label>
                <input className="glass-input" type="text" name="first_name" value={formData.first_name} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Last Name</label>
                <input className="glass-input" type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Email</label>
                <input className="glass-input" type="email" name="email" value={formData.email} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Phone</label>
                <input className="glass-input" type="text" name="phone" value={formData.phone} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Department</label>
                <select className="glass-select" name="department" value={formData.department} onChange={handleChange}>
                  <option value="">Select Department</option>
                  {departments.map((d) => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Position</label>
                <input className="glass-input" type="text" name="position" value={formData.position} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Employment Type</label>
                <select className="glass-select" name="employment_type" value={formData.employment_type} onChange={handleChange}>
                  <option value="full_time">Full Time</option>
                  <option value="part_time">Part Time</option>
                  <option value="contract">Contract</option>
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Salary</label>
                <input className="glass-input" type="number" name="salary" value={formData.salary} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Start Date</label>
                <input className="glass-input" type="date" name="start_date" value={formData.start_date} onChange={handleChange} />
              </div>
            </div>
            <button type="submit" className="login-button" style={{ width: 'auto', minWidth: '200px' }}>Add Staff</button>
          </form>
        </div>
      )}

      <div className="glass-card table-section">
        <div style={{ overflowX: 'auto' }}>
          <table className="glass-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Position</th>
                <th>Type</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: '600', color: '#fff' }}>Dr. Ahmed Bello</td>
                <td>ahmed.bello@university.edu</td>
                <td>Computer Science</td>
                <td>Senior Lecturer</td>
                <td>Full Time</td>
                <td><span className="status-badge status-active">Active</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: '600', color: '#fff' }}>Prof. Chidi Okoro</td>
                <td>chidi.okoro@university.edu</td>
                <td>Mathematics</td>
                <td>Professor</td>
                <td>Full Time</td>
                <td><span className="status-badge status-active">Active</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: '600', color: '#fff' }}>Mrs. Funke Adeyemi</td>
                <td>funke.adeyemi@university.edu</td>
                <td>Physics</td>
                <td>Lecturer I</td>
                <td>Part Time</td>
                <td><span className="status-badge status-active">Active</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="no-data" style={{ marginTop: '1.5rem', opacity: 0.6 }}>HR module ready. Connect to backend API for full functionality.</p>
      </div>
    </div>
  );
};

export default HR;
