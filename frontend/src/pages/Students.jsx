import { useState, useEffect } from 'react';
import { studentService } from '../services/api';
import { useToast } from '../components/toast/ToastContext';
import DataTable from '../components/DataTable';
import ConfirmModal from '../components/ConfirmModal';

const Students = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [faculties, setFaculties] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [programmes, setProgrammes] = useState([]);
  const [deleteModal, setDeleteModal] = useState({ open: false, id: null });
  const toast = useToast();
  const [formData, setFormData] = useState({
    username: '', email: '', password: '', first_name: '', last_name: '',
    phone: '', programme: '', level: '100', jamb_number: '',
    admission_year: new Date().getFullYear(), state_of_origin: '',
    guardian_name: '', guardian_phone: '',
  });

  useEffect(() => {
    fetchStudents();
    fetchDropdowns();
  }, []);

  const fetchStudents = async () => {
    try {
      const response = await studentService.getStudents();
      setStudents(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching students:', error);
      toast.error('Failed to fetch students');
    } finally {
      setLoading(false);
    }
  };

  const fetchDropdowns = async () => {
    try {
      const [fRes, dRes, pRes] = await Promise.all([
        studentService.getFaculties(), studentService.getDepartments(), studentService.getProgrammes()
      ]);
      setFaculties(fRes.data.results || fRes.data);
      setDepartments(dRes.data.results || dRes.data);
      setProgrammes(pRes.data.results || pRes.data);
    } catch (error) {
      console.error('Error fetching dropdowns:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await studentService.updateStudent(editingId, formData);
        toast.success('Student updated successfully!');
      } else {
        await studentService.createStudent(formData);
        toast.success('Student registered successfully!');
      }
      setShowForm(false);
      setEditingId(null);
      resetForm();
      fetchStudents();
    } catch (error) {
      console.error('Error saving student:', error);
      toast.error(error.response?.data ? JSON.stringify(error.response.data) : 'Error saving student');
    }
  };

  const handleEdit = (student) => {
    setEditingId(student.id);
    setFormData({
      username: student.user?.username || '', email: student.user?.email || '', password: '',
      first_name: student.user?.first_name || '', last_name: student.user?.last_name || '',
      phone: student.user?.phone || '', programme: student.programme || '',
      level: student.level?.toString() || '100', jamb_number: student.jamb_number || '',
      admission_year: student.admission_year || new Date().getFullYear(),
      state_of_origin: student.state_of_origin || '',
      guardian_name: student.guardian_name || '', guardian_phone: student.guardian_phone || '',
    });
    setShowForm(true);
  };

  const handleDelete = async () => {
    try {
      await studentService.deleteStudent(deleteModal.id);
      toast.success('Student deleted successfully!');
      setDeleteModal({ open: false, id: null });
      fetchStudents();
    } catch (error) {
      console.error('Error deleting student:', error);
      toast.error('Error deleting student');
    }
  };

  const handleBulkDelete = async (ids) => {
    try {
      await Promise.all(ids.map(id => studentService.deleteStudent(id)));
      toast.success(`${ids.length} students deleted successfully!`);
      fetchStudents();
    } catch (error) {
      console.error('Error bulk deleting:', error);
      toast.error('Error deleting students');
    }
  };

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const resetForm = () => {
    setEditingId(null);
    setFormData({
      username: '', email: '', password: '', first_name: '', last_name: '', phone: '',
      programme: '', level: '100', jamb_number: '', admission_year: new Date().getFullYear(),
      state_of_origin: '', guardian_name: '', guardian_phone: '',
    });
  };

  const columns = [
    { key: 'matric_number', label: 'Matric Number' },
    { key: 'name', label: 'Name', render: (row) => `${row.user?.first_name || ''} ${row.user?.last_name || ''}` },
    { key: 'programme_name', label: 'Programme' },
    { key: 'level', label: 'Level' },
    { key: 'status', label: 'Status', render: (row) => (
      <span className={`status-badge status-${row.status}`}>{row.status}</span>
    )},
    { key: 'admission_year', label: 'Year' },
    { key: 'actions', label: 'Actions', render: (row) => (
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button className="btn-action btn-edit" onClick={() => handleEdit(row)}>Edit</button>
        <button className="btn-action btn-delete" onClick={() => setDeleteModal({ open: true, id: row.id })}>Delete</button>
      </div>
    )},
  ];

  const filterOptions = [
    { key: 'status', label: 'All Status', options: [
      { value: 'active', label: 'Active' },
      { value: 'suspended', label: 'Suspended' },
      { value: 'graduated', label: 'Graduated' },
      { value: 'withdrawn', label: 'Withdrawn' },
    ]},
    { key: 'level', label: 'All Levels', options: [
      { value: '100', label: '100 Level' },
      { value: '200', label: '200 Level' },
      { value: '300', label: '300 Level' },
      { value: '400', label: '400 Level' },
      { value: '500', label: '500 Level' },
    ]},
  ];

  return (
    <div className="students-page">
      <div className="page-header">
        <h1 style={{ color: '#1e40af', fontWeight: 800, letterSpacing: '-0.03em', margin: 0, WebkitTextStroke: '1px rgba(59, 130, 246, 0.5)', textShadow: '2px 2px 0 rgba(59, 130, 246, 0.3), -1px -1px 0 rgba(59, 130, 246, 0.2), 1px -1px 0 rgba(59, 130, 246, 0.2), -1px 1px 0 rgba(59, 130, 246, 0.2)' }}>Students Management</h1>
        <button style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', color: 'white', border: 'none', borderRadius: '10px', padding: '0.75rem 1.25rem', fontWeight: 600, cursor: 'pointer', boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)' }} onClick={() => showForm ? (setShowForm(false), resetForm()) : setShowForm(true)}>
          {showForm ? 'Cancel' : 'Add Student'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card form-section">
          <h2 style={{ color: '#1e40af', marginBottom: '1.5rem', fontWeight: 700 }}>{editingId ? 'Edit Student' : 'New Student Registration'}</h2>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              <div className="form-group">
                <label className="glass-label">First Name *</label>
                <input className="glass-input" type="text" name="first_name" value={formData.first_name} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Last Name *</label>
                <input className="glass-input" type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
              </div>
              {!editingId && (
                <>
                  <div className="form-group">
                    <label className="glass-label">Username *</label>
                    <input className="glass-input" type="text" name="username" value={formData.username} onChange={handleChange} required />
                  </div>
                  <div className="form-group">
                    <label className="glass-label">Email *</label>
                    <input className="glass-input" type="email" name="email" value={formData.email} onChange={handleChange} required />
                  </div>
                  <div className="form-group">
                    <label className="glass-label">Password *</label>
                    <input className="glass-input" type="password" name="password" value={formData.password} onChange={handleChange} required={!editingId} />
                  </div>
                </>
              )}
              <div className="form-group">
                <label className="glass-label">Phone</label>
                <input className="glass-input" type="text" name="phone" value={formData.phone} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Programme *</label>
                <select className="glass-select" name="programme" value={formData.programme} onChange={handleChange} required>
                  <option value="">Select Programme</option>
                  {programmes.map(p => <option key={p.id} value={p.id}>{p.name} ({p.code})</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Level</label>
                <select className="glass-select" name="level" value={formData.level} onChange={handleChange}>
                  {[100,200,300,400,500].map(l => <option key={l} value={l}>{l} Level</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">JAMB Number</label>
                <input className="glass-input" type="text" name="jamb_number" value={formData.jamb_number} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Admission Year</label>
                <input className="glass-input" type="number" name="admission_year" value={formData.admission_year} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">State of Origin</label>
                <input className="glass-input" type="text" name="state_of_origin" value={formData.state_of_origin} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Guardian Name</label>
                <input className="glass-input" type="text" name="guardian_name" value={formData.guardian_name} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Guardian Phone</label>
                <input className="glass-input" type="text" name="guardian_phone" value={formData.guardian_phone} onChange={handleChange} />
              </div>
            </div>
            <button type="submit" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', color: 'white', border: 'none', borderRadius: '10px', padding: '0.75rem 1.5rem', fontWeight: 600, cursor: 'pointer' }}>
              {editingId ? 'Update Student' : 'Register Student'}
            </button>
          </form>
        </div>
      )}

      <DataTable
        data={students}
        columns={columns}
        loading={loading}
        searchable
        searchKeys={['matric_number', 'user.first_name', 'user.last_name', 'programme_name']}
        filterOptions={filterOptions}
        onBulkDelete={handleBulkDelete}
        onBulkExport
        exportFilename="students"
        emptyMessage="No students found"
      />

      <ConfirmModal
        isOpen={deleteModal.open}
        title="Delete Student"
        message="Are you sure you want to delete this student? This action cannot be undone."
        onConfirm={handleDelete}
        onCancel={() => setDeleteModal({ open: false, id: null })}
      />
    </div>
  );
};

export default Students;
