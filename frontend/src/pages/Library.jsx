import { useState, useEffect } from 'react';
import { libraryService } from '../services/api';

const Library = () => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    isbn: '',
    category: '',
    quantity: 1,
    available: 1,
    shelf_location: '',
  });

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    try {
      const response = await libraryService.getBooks();
      setBooks(response.data.results || []);
    } catch (error) {
      console.error('Error fetching books:', error);
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await libraryService.createBook(formData);
      setShowForm(false);
      setFormData({ title: '', author: '', isbn: '', category: '', quantity: 1, available: 1, shelf_location: '' });
      await fetchBooks();
    } catch (error) {
      console.error('Error creating book:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const categories = ['Textbook', 'Reference', 'Journal', 'Magazine', 'Novel', 'Research'];

  return (
    <div className="students-page">
      <div className="page-header">
        <h1>Library Management</h1>
        <button className="login-button" style={{ width: 'auto', marginTop: 0 }} onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Book'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card form-section">
          <h2>Add New Book</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="glass-label">Title</label>
                <input className="glass-input" type="text" name="title" value={formData.title} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">Author</label>
                <input className="glass-input" type="text" name="author" value={formData.author} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="glass-label">ISBN</label>
                <input className="glass-input" type="text" name="isbn" value={formData.isbn} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="glass-label">Category</label>
                <select className="glass-select" name="category" value={formData.category} onChange={handleChange} required>
                  <option value="">Select Category</option>
                  {categories.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="glass-label">Quantity</label>
                <input className="glass-input" type="number" name="quantity" value={formData.quantity} onChange={handleChange} min="1" />
              </div>
              <div className="form-group">
                <label className="glass-label">Shelf Location</label>
                <input className="glass-input" type="text" name="shelf_location" value={formData.shelf_location} onChange={handleChange} />
              </div>
            </div>
            <button type="submit" className="login-button" style={{ width: 'auto', minWidth: '200px' }}>Add Book</button>
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
                  <th>Title</th>
                  <th>Author</th>
                  <th>ISBN</th>
                  <th>Category</th>
                  <th>Available</th>
                  <th>Shelf</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ fontWeight: '600', color: '#fff' }}>Introduction to Computer Science</td>
                  <td>John Smith</td>
                  <td>978-0-123456-78-9</td>
                  <td>Textbook</td>
                  <td>5</td>
                  <td>A-101</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: '600', color: '#fff' }}>Data Structures and Algorithms</td>
                  <td>Jane Doe</td>
                  <td>978-0-987654-32-1</td>
                  <td>Textbook</td>
                  <td>3</td>
                  <td>A-102</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
        <p className="no-data" style={{ marginTop: '1.5rem', opacity: 0.6 }}>Library module ready. Connect to backend API for full functionality.</p>
      </div>
    </div>
  );
};

export default Library;
