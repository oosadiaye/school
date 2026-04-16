import { useState } from 'react';

const Users = () => {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    user_type: 'staff',
    is_active: true,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    alert('User added successfully!');
    setShowForm(false);
    setFormData({ username: '', email: '', password: '', first_name: '', last_name: '', user_type: 'staff', is_active: true });
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const users = [
    { id: 1, username: 'admin', name: 'System Administrator', email: 'admin@school.edu', user_type: 'admin', status: 'Active' },
    { id: 2, username: 'ahmed.bello', name: 'Ahmed Bello', email: 'ahmed.bello@school.edu', user_type: 'staff', status: 'Active' },
    { id: 3, username: 'chidi.okoro', name: 'Chidi Okoro', email: 'chidi.okoro@school.edu', user_type: 'staff', status: 'Active' },
    { id: 4, username: 'student001', name: 'John Doe', email: 'student001@school.edu', user_type: 'student', status: 'Active' },
    { id: 5, username: 'student002', name: 'Jane Smith', email: 'student002@school.edu', user_type: 'student', status: 'Active' },
  ];

  return (
    <div className="students-page">
      <div className="page-header">
        <h1>User Management</h1>
        <button className="login-button" style={{ width: 'auto', marginTop: 0 }} onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add User'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card form-section">
          <h2>Add New User</h2>
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
                <label className="glass-label">Username</label>
                <input className="glass-input" type="text" name="username" value={formData.username} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Email</label>
                <input className="glass-input" type="email" name="email" value={formData.email} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Password</label>
                <input className="glass-input" type="password" name="password" value={formData.password} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">User Type</label>
                <select className="glass-select" name="user_type" value={formData.user_type} onChange={handleChange}>
                  <option value="student">Student</option>
                  <option value="staff">Staff</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>
            <button type="submit" className="login-button" style={{ width: 'auto', minWidth: '200px' }}>Add User</button>
          </form>
        </div>
      )}

      <div className="glass-card table-section">
        <div style={{ overflowX: 'auto' }}>
          <table className="glass-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Name</th>
                <th>Email</th>
                <th>User Type</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td style={{ fontWeight: '600', color: 'var(--primary-blue)' }}>{user.username}</td>
                  <td style={{ fontWeight: '600', color: '#fff' }}>{user.name}</td>
                  <td>{user.email}</td>
                  <td><span className={`status-badge status-${user.user_type}`}>{user.user_type}</span></td>
                  <td><span className="status-badge status-active">{user.status}</span></td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button className="btn-action btn-edit">Edit</button>
                      <button className="btn-action btn-delete">Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="no-data" style={{ marginTop: '1.5rem', opacity: 0.6 }}>User management module ready.</p>
      </div>
    </div>
  );
};

export default Users;
