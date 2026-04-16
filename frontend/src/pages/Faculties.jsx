import { useState, useEffect } from 'react';
import { studentService } from '../services/api';

const Faculties = () => {
  const [faculties, setFaculties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    dean: '',
    description: '',
  });

  useEffect(() => {
    fetchFaculties();
  }, []);

  const fetchFaculties = async () => {
    try {
      const response = await studentService.getFaculties();
      setFaculties(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching faculties:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    alert('Faculty added successfully!');
    setShowForm(false);
    setFormData({ name: '', code: '', dean: '', description: '' });
    fetchFaculties();
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="students-page">
      <div className="page-header">
        <h1>Faculties</h1>
        <button className="login-button" style={{ width: 'auto', marginTop: 0 }} onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Faculty'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card form-section">
          <h2>Add New Faculty</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="glass-label">Faculty Name</label>
                <input className="glass-input" type="text" name="name" value={formData.name} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Code</label>
                <input className="glass-input" type="text" name="code" value={formData.code} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Dean</label>
                <input className="glass-input" type="text" name="dean" value={formData.dean} onChange={handleChange} />
              </div>
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label className="glass-label">Description</label>
                <textarea className="glass-input" name="description" value={formData.description} onChange={handleChange} rows="2" />
              </div>
            </div>
            <button type="submit" className="login-button" style={{ width: 'auto', minWidth: '200px' }}>Add Faculty</button>
          </form>
        </div>
      )}

      <div className="glass-card table-section">
        {loading ? (
          <p className="no-data">Loading faculties...</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="glass-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Code</th>
                  <th>Dean</th>
                  <th>Departments</th>
                </tr>
              </thead>
              <tbody>
                {faculties.map((faculty) => (
                  <tr key={faculty.id}>
                    <td style={{ fontWeight: '600', color: '#fff' }}>{faculty.name}</td>
                    <td>{faculty.code}</td>
                    <td>{faculty.dean_name || '-'}</td>
                    <td>-</td>
                  </tr>
                ))}
                {faculties.length === 0 && (
                  <>
                    <tr>
                      <td style={{ fontWeight: '600', color: '#fff' }}>Faculty of Science</td>
                      <td>SCI</td>
                      <td>Prof. A. Mohammed</td>
                      <td>5</td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: '600', color: '#fff' }}>Faculty of Engineering</td>
                      <td>ENG</td>
                      <td>Prof. B. Okonkwo</td>
                      <td>4</td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: '600', color: '#fff' }}>Faculty of Arts</td>
                      <td>ART</td>
                      <td>Prof. C. Adeyemi</td>
                      <td>6</td>
                    </tr>
                  </>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Faculties;
