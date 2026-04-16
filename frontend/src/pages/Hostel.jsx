import { useState, useEffect } from 'react';

const Hostel = () => {
  const [hostels, setHostels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    gender: 'male',
    capacity: 100,
    available_beds: 100,
    location: '',
    warden_name: '',
    warden_phone: '',
  });

  useEffect(() => {
    setLoading(false);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    alert('Hostel added successfully!');
    setShowForm(false);
    setFormData({ name: '', gender: 'male', capacity: 100, available_beds: 100, location: '', warden_name: '', warden_phone: '' });
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="students-page">
      <div className="page-header">
        <h1>Hostel Management</h1>
        <button className="login-button" style={{ width: 'auto', marginTop: 0 }} onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Hostel'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card form-section">
          <h2>Add New Hostel</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="glass-label">Hostel Name</label>
                <input className="glass-input" type="text" name="name" value={formData.name} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Gender</label>
                <select className="glass-select" name="gender" value={formData.gender} onChange={handleChange}>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Capacity</label>
                <input className="glass-input" type="number" name="capacity" value={formData.capacity} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Location</label>
                <input className="glass-input" type="text" name="location" value={formData.location} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Warden Name</label>
                <input className="glass-input" type="text" name="warden_name" value={formData.warden_name} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Warden Phone</label>
                <input className="glass-input" type="text" name="warden_phone" value={formData.warden_phone} onChange={handleChange} />
              </div>
            </div>
            <button type="submit" className="login-button" style={{ width: 'auto', minWidth: '200px' }}>Add Hostel</button>
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
                  <th>Hostel Name</th>
                  <th>Gender</th>
                  <th>Capacity</th>
                  <th>Available</th>
                  <th>Location</th>
                  <th>Warden</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ fontWeight: '600', color: '#fff' }}>Hall A - Male</td>
                  <td>Male</td>
                  <td>200</td>
                  <td>45</td>
                  <td>North Campus</td>
                  <td>Mr. Adekunle</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: '600', color: '#fff' }}>Hall B - Female</td>
                  <td>Female</td>
                  <td>180</td>
                  <td>20</td>
                  <td>South Campus</td>
                  <td>Mrs. Okonkwo</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
        <p className="no-data" style={{ marginTop: '1.5rem', opacity: 0.6 }}>Hostel module ready. Connect to backend API for full functionality.</p>
      </div>
    </div>
  );
};

export default Hostel;
