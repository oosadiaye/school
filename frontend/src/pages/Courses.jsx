import { useState, useEffect } from 'react';
import { academicService, studentService } from '../services/api';
import { useToast } from '../components/toast/ToastContext';
import DataTable from '../components/DataTable';
import ConfirmModal from '../components/ConfirmModal';

const Courses = () => {
  const [courses, setCourses] = useState([]);
  const [programmes, setProgrammes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [deleteModal, setDeleteModal] = useState({ open: false, id: null });
  const toast = useToast();
  const [formData, setFormData] = useState({
    programme: '', code: '', name: '', credit_units: 3, level: '100', semester: 'first', description: '',
  });

  useEffect(() => { fetchCourses(); fetchProgrammes(); }, []);

  const fetchCourses = async () => {
    try {
      const response = await academicService.getCourses();
      setCourses(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching courses:', error);
      toast.error('Failed to fetch courses');
    } finally {
      setLoading(false);
    }
  };

  const fetchProgrammes = async () => {
    try {
      const response = await studentService.getProgrammes();
      setProgrammes(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching programmes:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await academicService.createCourse(formData);
      toast.success('Course created successfully!');
      setShowForm(false);
      setFormData({ programme: '', code: '', name: '', credit_units: 3, level: '100', semester: 'first', description: '' });
      fetchCourses();
    } catch (error) {
      console.error('Error creating course:', error);
      toast.error('Error creating course');
    }
  };

  const handleDelete = async () => {
    try {
      await academicService.deleteCourse?.(deleteModal.id);
      toast.success('Course deleted successfully!');
      setDeleteModal({ open: false, id: null });
      fetchCourses();
    } catch (error) {
      console.error('Error deleting course:', error);
      toast.error('Error deleting course');
    }
  };

  const columns = [
    { key: 'code', label: 'Code' },
    { key: 'name', label: 'Course Name' },
    { key: 'programme_name', label: 'Programme' },
    { key: 'credit_units', label: 'Credits' },
    { key: 'level', label: 'Level' },
    { key: 'semester', label: 'Semester', render: (row) => row.semester?.charAt(0).toUpperCase() + row.semester?.slice(1) },
    { key: 'actions', label: 'Actions', render: (row) => (
      <button className="btn-action btn-delete" onClick={() => setDeleteModal({ open: true, id: row.id })}>Delete</button>
    )},
  ];

  const filterOptions = [
    { key: 'level', label: 'All Levels', options: [
      { value: '100', label: '100 Level' }, { value: '200', label: '200 Level' },
      { value: '300', label: '300 Level' }, { value: '400', label: '400 Level' }, { value: '500', label: '500 Level' },
    ]},
    { key: 'semester', label: 'All Semesters', options: [
      { value: 'first', label: 'First' }, { value: 'second', label: 'Second' },
    ]},
  ];

  return (
    <div className="courses-page">
      <div className="page-header">
        <h1 style={{ color: '#1e40af', fontWeight: 800, letterSpacing: '-0.03em', margin: 0, WebkitTextStroke: '1px rgba(59, 130, 246, 0.5)', textShadow: '2px 2px 0 rgba(59, 130, 246, 0.3)' }}>Course Management</h1>
        <button style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', color: 'white', border: 'none', borderRadius: '10px', padding: '0.75rem 1.25rem', fontWeight: 600, cursor: 'pointer' }} onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Course'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card form-section">
          <h2 style={{ color: '#1e40af', marginBottom: '1.5rem' }}>Create New Course</h2>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              <div className="form-group">
                <label className="glass-label">Programme *</label>
                <select className="glass-select" name="programme" value={formData.programme} onChange={(e) => setFormData({ ...formData, programme: e.target.value })} required>
                  <option value="">Select Programme</option>
                  {programmes.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Course Code *</label>
                <input className="glass-input" type="text" name="code" value={formData.code} onChange={(e) => setFormData({ ...formData, code: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Course Name *</label>
                <input className="glass-input" type="text" name="name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Credit Units</label>
                <input className="glass-input" type="number" name="credit_units" value={formData.credit_units} onChange={(e) => setFormData({ ...formData, credit_units: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="glass-label">Level</label>
                <select className="glass-select" name="level" value={formData.level} onChange={(e) => setFormData({ ...formData, level: e.target.value })}>
                  {[100,200,300,400,500].map(l => <option key={l} value={l}>{l} Level</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Semester</label>
                <select className="glass-select" name="semester" value={formData.semester} onChange={(e) => setFormData({ ...formData, semester: e.target.value })}>
                  <option value="first">First</option>
                  <option value="second">Second</option>
                </select>
              </div>
            </div>
            <button type="submit" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', color: 'white', border: 'none', borderRadius: '10px', padding: '0.75rem 1.5rem', fontWeight: 600, cursor: 'pointer' }}>Create Course</button>
          </form>
        </div>
      )}

      <DataTable
        data={courses}
        columns={columns}
        loading={loading}
        searchable
        searchKeys={['code', 'name', 'programme_name']}
        filterOptions={filterOptions}
        onBulkExport
        exportFilename="courses"
        emptyMessage="No courses found"
      />

      <ConfirmModal
        isOpen={deleteModal.open}
        title="Delete Course"
        message="Are you sure you want to delete this course?"
        onConfirm={handleDelete}
        onCancel={() => setDeleteModal({ open: false, id: null })}
      />
    </div>
  );
};

export default Courses;
