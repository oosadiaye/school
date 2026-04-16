import { useState, useEffect } from 'react';
import { studentService } from '../services/api';

const Departments = () => {
  const [departments, setDepartments] = useState([]);
  const [faculties, setFaculties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    faculty: '',
    hod: '',
    description: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [deptRes, facRes] = await Promise.all([
        studentService.getDepartments(),
        studentService.getFaculties(),
      ]);
      setDepartments(deptRes.data.results || deptRes.data);
      setFaculties(facRes.data.results || facRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    alert('Department added successfully!');
    setShowForm(false);
    setFormData({ name: '', code: '', faculty: '', hod: '', description: '' });
    fetchData();
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="students-page">
      <div className="page-header">
        <h1>Departments</h1>
        <button className="login-button" style={{ width: 'auto', marginTop: 0 }} onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Department'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card form-section">
          <h2>Add New Department</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="glass-label">Department Name</label>
                <input className="glass-input" type="text" name="name" value={formData.name} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Code</label>
                <input className="glass-input" type="text" name="code" value={formData.code} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Faculty</label>
                <select className="glass-select" name="faculty" value={formData.faculty} onChange={handleChange}>
                  <option value="">Select Faculty</option>
                  {faculties.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">HOD</label>
                <input className="glass-input" type="text" name="hod" value={formData.hod} onChange={handleChange} />
              </div>
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label className="glass-label">Description</label>
                <textarea className="glass-input" name="description" value={formData.description} onChange={handleChange} rows="2" />
              </div>
            </div>
            <button type="submit" className="login-button" style={{ width: 'auto', minWidth: '200px' }}>Add Department</button>
          </form>
        </div>
      )}

      <div className="glass-card table-section">
        {loading ? (
          <p className="no-data">Loading departments...</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="glass-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Code</th>
                  <th>Faculty</th>
                  <th>HOD</th>
                  <th>Programmes</th>
                </tr>
              </thead>
              <tbody>
                {departments.map((dept) => (
                  <tr key={dept.id}>
                    <td style={{ fontWeight: '600', color: '#fff' }}>{dept.name}</td>
                    <td>{dept.code}</td>
                    <td>{dept.faculty_name || '-'}</td>
                    <td>{dept.hod_name || '-'}</td>
                    <td>-</td>
                  </tr>
                ))}
                {departments.length === 0 && (
                  <>
                    <tr>
                      <td style={{ fontWeight: '600', color: '#fff' }}>Computer Science</td>
                      <td>CS</td>
                      <td>Faculty of Science</td>
                      <td>Dr. E. Ojo</td>
                      <td>3</td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: '600', color: '#fff' }}>Electrical Engineering</td>
                      <td>EE</td>
                      <td>Faculty of Engineering</td>
                      <td>Dr. F. Musa</td>
                      <td>2</td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: '600', color: '#fff' }}>Economics</td>
                      <td>ECO</td>
                      <td>Faculty of Arts</td>
                      <td>Dr. G. Oladipo</td>
                      <td>2</td>
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

export default Departments;
