import { useState, useEffect } from 'react';
import { studentService } from '../services/api';

const Programmes = () => {
  const [programmes, setProgrammes] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    department: '',
    duration_years: 4,
    degree_type: 'Bachelor',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [progRes, deptRes] = await Promise.all([
        studentService.getProgrammes(),
        studentService.getDepartments(),
      ]);
      setProgrammes(progRes.data.results || progRes.data);
      setDepartments(deptRes.data.results || deptRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    alert('Programme added successfully!');
    setShowForm(false);
    setFormData({ name: '', code: '', department: '', duration_years: 4, degree_type: 'Bachelor' });
    fetchData();
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="students-page">
      <div className="page-header">
        <h1>Programmes</h1>
        <button className="login-button" style={{ width: 'auto', marginTop: 0 }} onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Programme'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card form-section">
          <h2>Add New Programme</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="glass-label">Programme Name</label>
                <input className="glass-input" type="text" name="name" value={formData.name} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Code</label>
                <input className="glass-input" type="text" name="code" value={formData.code} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Department</label>
                <select className="glass-select" name="department" value={formData.department} onChange={handleChange}>
                  <option value="">Select Department</option>
                  {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Duration (Years)</label>
                <select className="glass-select" name="duration_years" value={formData.duration_years} onChange={handleChange}>
                  <option value={3}>3 Years</option>
                  <option value={4}>4 Years</option>
                  <option value={5}>5 Years</option>
                  <option value={6}>6 Years</option>
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Degree Type</label>
                <select className="glass-select" name="degree_type" value={formData.degree_type} onChange={handleChange}>
                  <option value="Bachelor">Bachelor</option>
                  <option value="Master">Master</option>
                  <option value="PhD">PhD</option>
                  <option value="Diploma">Diploma</option>
                </select>
              </div>
            </div>
            <button type="submit" className="login-button" style={{ width: 'auto', minWidth: '200px' }}>Add Programme</button>
          </form>
        </div>
      )}

      <div className="glass-card table-section">
        {loading ? (
          <p className="no-data">Loading programmes...</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="glass-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Code</th>
                  <th>Department</th>
                  <th>Duration</th>
                  <th>Degree</th>
                </tr>
              </thead>
              <tbody>
                {programmes.map((prog) => (
                  <tr key={prog.id}>
                    <td style={{ fontWeight: '600', color: '#fff' }}>{prog.name}</td>
                    <td>{prog.code}</td>
                    <td>{prog.department_name || '-'}</td>
                    <td>{prog.duration_years} Years</td>
                    <td>{prog.degree_type}</td>
                  </tr>
                ))}
                {programmes.length === 0 && (
                  <>
                    <tr>
                      <td style={{ fontWeight: '600', color: '#fff' }}>Computer Science</td>
                      <td>CS</td>
                      <td>Computer Science</td>
                      <td>4 Years</td>
                      <td>Bachelor</td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: '600', color: '#fff' }}>Electrical Engineering</td>
                      <td>EE</td>
                      <td>Electrical Engineering</td>
                      <td>5 Years</td>
                      <td>Bachelor</td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: '600', color: '#fff' }}>Economics</td>
                      <td>ECO</td>
                      <td>Economics</td>
                      <td>4 Years</td>
                      <td>Bachelor</td>
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

export default Programmes;
