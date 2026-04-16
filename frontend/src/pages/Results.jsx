import { useState, useEffect } from 'react';
import { academicService, studentService } from '../services/api';
import './Results.css';

const Results = () => {
  const [results, setResults] = useState([]);
  const [students, setStudents] = useState([]);
  const [courses, setCourses] = useState([]);
  const [semesters, setSemesters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [gpaData, setGpaData] = useState(null);
  const [formData, setFormData] = useState({
    student: '',
    course: '',
    semester: '',
    ca_score: '',
    exam_score: '',
    remark: '',
  });

  useEffect(() => {
    fetchResults();
    fetchDropdowns();
  }, []);

  const fetchResults = async () => {
    try {
      const response = await academicService.getResults();
      setResults(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDropdowns = async () => {
    try {
      const [studentsRes, coursesRes, semestersRes] = await Promise.all([
        studentService.getStudents(),
        academicService.getCourses(),
        academicService.getSemesters(),
      ]);
      setStudents(studentsRes.data.results || studentsRes.data);
      setCourses(coursesRes.data.results || coursesRes.data);
      setSemesters(semestersRes.data.results || semestersRes.data);
    } catch (error) {
      console.error('Error fetching dropdowns:', error);
    }
  };

  const calculateGPA = async (studentId) => {
    try {
      const response = await academicService.calculateGPA(studentId);
      setGpaData(response.data);
    } catch (error) {
      console.error('Error calculating GPA:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await academicService.createResult(formData);
      setShowForm(false);
      setFormData({
        student: '',
        course: '',
        semester: '',
        ca_score: '',
        exam_score: '',
        remark: '',
      });
      fetchResults();
    } catch (error) {
      console.error('Error creating result:', error);
      alert('Error creating result');
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const getGradeColor = (grade) => {
    const colors = {
      'A': '#28a745',
      'B': '#17a2b8',
      'C': '#ffc107',
      'D': '#fd7e14',
      'E': '#dc3545',
      'F': '#dc3545',
    };
    return colors[grade] || '#6c757d';
  };

  return (
    <div className="results-page">
      <div className="page-header">
        <h1>Results Management</h1>
        <button className="login-button" style={{ width: 'auto', marginTop: 0 }} onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Enter Result'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card form-section">
          <h2>Enter Student Result</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="glass-label">Student</label>
                <select className="glass-select" name="student" value={formData.student} onChange={handleChange} required>
                  <option value="">Select Student</option>
                  {students.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.matric_number} - {s.user?.first_name} {s.user?.last_name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Course</label>
                <select className="glass-select" name="course" value={formData.course} onChange={handleChange} required>
                  <option value="">Select Course</option>
                  {courses.map((c) => (
                    <option key={c.id} value={c.id}>{c.code} - {c.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Semester</label>
                <select className="glass-select" name="semester" value={formData.semester} onChange={handleChange} required>
                  <option value="">Select Semester</option>
                  {semesters.map((s) => (
                    <option key={s.id} value={s.id}>{s.session_name} - {s.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">CA Score</label>
                <input className="glass-input" type="number" name="ca_score" value={formData.ca_score} onChange={handleChange} max="40" />
              </div>
              <div className="form-group">
                <label className="glass-label">Exam Score</label>
                <input className="glass-input" type="number" name="exam_score" value={formData.exam_score} onChange={handleChange} max="60" />
              </div>
              <div className="form-group">
                <label className="glass-label">Remark</label>
                <input className="glass-input" type="text" name="remark" value={formData.remark} onChange={handleChange} />
              </div>
            </div>
            <button type="submit" className="login-button" style={{ width: 'auto', minWidth: '200px' }}>Submit Result</button>
          </form>
        </div>
      )}

      {gpaData && (
        <div className="gpa-card">
          <h3>GPA Information</h3>
          <p>GPA: <strong>{gpaData.gpa}</strong></p>
          <p>Total Credits: {gpaData.total_credits}</p>
          <p>Courses: {gpaData.results_count}</p>
        </div>
      )}

      <div className="glass-card table-section">
        {loading ? (
          <p className="no-data">Loading results data...</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="glass-table">
              <thead>
                <tr>
                  <th>Matric Number</th>
                  <th>Student Name</th>
                  <th>Course</th>
                  <th>CA</th>
                  <th>Exam</th>
                  <th>Total</th>
                  <th>Grade</th>
                  <th>GP</th>
                  <th>Published</th>
                </tr>
              </thead>
              <tbody>
                {results.map((result) => (
                  <tr key={result.id}>
                    <td>{result.student_matric}</td>
                    <td style={{ fontWeight: '600', color: '#fff' }}>{result.student_name}</td>
                    <td>{result.course_code}<br /><small style={{ color: 'rgba(255,255,255,0.5)' }}>{result.course_name}</small></td>
                    <td>{result.ca_score || '-'}</td>
                    <td>{result.exam_score || '-'}</td>
                    <td style={{ fontWeight: '700', color: 'var(--primary-blue)' }}>{result.total_score || '-'}</td>
                    <td>
                      <span className="grade-badge" style={{ backgroundColor: getGradeColor(result.grade) }}>
                        {result.grade || '-'}
                      </span>
                    </td>
                    <td>{result.grade_point || '-'}</td>
                    <td>
                      <span style={{ color: result.is_published ? '#4ade80' : '#f87171' }}>
                        {result.is_published ? 'Yes' : 'No'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {results.length === 0 && !loading && (
          <p className="no-data">No results found.</p>
        )}
      </div>
    </div>
  );
};

export default Results;
