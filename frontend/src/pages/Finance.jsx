import { useState, useEffect } from 'react';
import { financeService, studentService } from '../services/api';

const Finance = () => {
  const [activeTab, setActiveTab] = useState('feeStructures');
  const [feeTypes, setFeeTypes] = useState([]);
  const [feeStructures, setFeeStructures] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [programmes, setProgrammes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [dashboard, setDashboard] = useState(null);

  const [formData, setFormData] = useState({
    name: '', amount: '', programme: '', level: '', session: '', fee_type: '', is_mandatory: true
  });

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [ftRes, fsRes, progRes, dashRes] = await Promise.all([
        financeService.getFeeTypes(),
        financeService.getFeeStructures(),
        studentService.getProgrammes(),
        financeService.getFinanceDashboard()
      ]);
      setFeeTypes(ftRes.data.results || ftRes.data);
      setFeeStructures(fsRes.data.results || fsRes.data);
      setProgrammes(progRes.data.results || progRes.data);
      setDashboard(dashRes.data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (activeTab === 'feeTypes') {
        await financeService.createFeeType({ name: formData.name });
      } else if (activeTab === 'feeStructures') {
        await financeService.createFeeStructure({
          fee_type: formData.fee_type,
          programme: formData.programme,
          amount: formData.amount,
          level: formData.level,
          session: formData.session,
          is_mandatory: formData.is_mandatory
        });
      }
      setShowForm(false);
      fetchData();
    } catch (error) {
      alert('Error creating item');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      paid: '#28a745', partially_paid: '#ffc107', pending: '#17a2b8', overdue: '#dc3545', waived: '#6c757d'
    };
    return colors[status] || '#6c757d';
  };

  return (
    <div className="finance-page">
      <div className="page-header">
        <h1 style={{ color: '#1e40af', fontWeight: 800, letterSpacing: '-0.03em', margin: 0, WebkitTextStroke: '1px rgba(59, 130, 246, 0.5)', textShadow: '2px 2px 0 rgba(59, 130, 246, 0.3), -1px -1px 0 rgba(59, 130, 246, 0.2), 1px -1px 0 rgba(59, 130, 246, 0.2), -1px 1px 0 rgba(59, 130, 246, 0.2)' }}>Finance Management</h1>
      </div>

      {dashboard && (
        <div className="glass-stats-grid" style={{ marginBottom: '2.5rem' }}>
          <div className="glass-stat-card">
            <div className="glass-stat-icon" style={{ background: 'rgba(34, 197, 94, 0.15)', color: '#4ade80' }}>₦</div>
            <div className="glass-stat-info">
              <h3>₦{dashboard.total_collected?.toLocaleString()}</h3>
              <p>Total Collected</p>
            </div>
          </div>
          <div className="glass-stat-card">
            <div className="glass-stat-icon" style={{ background: 'rgba(234, 179, 8, 0.15)', color: '#facc15' }}>📋</div>
            <div className="glass-stat-info">
              <h3>₦{dashboard.total_pending?.toLocaleString()}</h3>
              <p>Total Pending</p>
            </div>
          </div>
          <div className="glass-stat-card">
            <div className="glass-stat-icon" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>📊</div>
            <div className="glass-stat-info">
              <h3>{dashboard.collection_rate}%</h3>
              <p>Collection Rate</p>
            </div>
          </div>
        </div>
      )}

      <div className="glass-tabs">
        <button className={`glass-tab ${activeTab === 'feeTypes' ? 'active' : ''}`} onClick={() => setActiveTab('feeTypes')}>Fee Types</button>
        <button className={`glass-tab ${activeTab === 'feeStructures' ? 'active' : ''}`} onClick={() => setActiveTab('feeStructures')}>Fee Structures</button>
        <button className={`glass-tab ${activeTab === 'invoices' ? 'active' : ''}`} onClick={() => setActiveTab('invoices')}>Invoices</button>
        <button className={`glass-tab ${activeTab === 'payments' ? 'active' : ''}`} onClick={() => setActiveTab('payments')}>Payments</button>
      </div>

      <div className="tab-content">
        <div className="page-header" style={{ marginBottom: '1.5rem', marginTop: 0 }}>
          <h2 style={{ color: '#1e40af', fontSize: '1.5rem', fontWeight: 700, textShadow: '1px 1px 0 rgba(59, 130, 246, 0.2)' }}>
            {activeTab === 'feeTypes' ? 'Fee Types' : activeTab === 'feeStructures' ? 'Fee Structures' : activeTab === 'invoices' ? 'Invoices' : 'Payments'}
          </h2>
          <button className="login-button" style={{ width: 'auto', marginTop: 0 }} onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : 'Add New'}
          </button>
        </div>

        {showForm && (
          <div className="glass-card form-section">
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                {activeTab === 'feeTypes' ? (
                  <div className="form-group">
                    <label className="glass-label">Fee Type Name</label>
                    <input className="glass-input" type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} required />
                  </div>
                ) : (
                  <>
                    <div className="form-group">
                      <label className="glass-label">Programme</label>
                      <select className="glass-select" value={formData.programme} onChange={(e) => setFormData({ ...formData, programme: e.target.value })} required>
                        <option value="">Select</option>
                        {programmes.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="glass-label">Fee Type</label>
                      <select className="glass-select" value={formData.fee_type} onChange={(e) => setFormData({ ...formData, fee_type: e.target.value })} required>
                        <option value="">Select</option>
                        {feeTypes.map(ft => <option key={ft.id} value={ft.id}>{ft.name}</option>)}
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="glass-label">Amount</label>
                      <input className="glass-input" type="number" value={formData.amount} onChange={(e) => setFormData({ ...formData, amount: e.target.value })} required />
                    </div>
                    <div className="form-group">
                      <label className="glass-label">Level</label>
                      <select className="glass-select" value={formData.level} onChange={(e) => setFormData({ ...formData, level: e.target.value })} required>
                        <option value="">Select</option>
                        <option value="100">100 Level</option>
                        <option value="200">200 Level</option>
                        <option value="300">300 Level</option>
                        <option value="400">400 Level</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="glass-label">Session</label>
                      <input className="glass-input" type="text" value={formData.session} onChange={(e) => setFormData({ ...formData, session: e.target.value })} placeholder="2025/2026" required />
                    </div>
                  </>
                )}
              </div>
              <button type="submit" className="login-button" style={{ width: 'auto', minWidth: '180px', marginTop: '1.5rem' }}>Submit</button>
            </form>
          </div>
        )}

        <div className="glass-card table-section">
          {loading ? (
            <p className="no-data">Loading data...</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="glass-table">
                <thead>
                  <tr>
                    {activeTab === 'feeTypes' && <th>Name</th>}
                    {activeTab === 'feeStructures' && <><th>Programme</th><th>Fee Type</th><th>Amount</th><th>Level</th><th>Session</th></>}
                    {activeTab === 'invoices' && <><th>Matric</th><th>Fee Type</th><th>Amount</th><th>Paid</th><th>Balance</th><th>Status</th></>}
                    {activeTab === 'payments' && <><th>Transaction ID</th><th>Matric</th><th>Amount</th><th>Method</th><th>Date</th><th>Status</th></>}
                  </tr>
                </thead>
                <tbody>
                  {activeTab === 'feeTypes' && feeTypes.map(ft => (
                    <tr key={ft.id}>
                      <td style={{ fontWeight: '600', color: '#1e40af' }}>{ft.name}</td>
                    </tr>
                  ))}
                  {activeTab === 'feeStructures' && feeStructures.map(fs => (
                    <tr key={fs.id}>
                      <td style={{ fontWeight: '600', color: '#1e40af' }}>{fs.programme_name}</td>
                      <td>{fs.fee_type_name}</td>
                      <td style={{ fontWeight: '700', color: 'var(--primary-blue)' }}>₦{parseFloat(fs.amount).toLocaleString()}</td>
                      <td>{fs.level}</td>
                      <td>{fs.session}</td>
                    </tr>
                  ))}
                  {activeTab === 'invoices' && invoices.map(inv => (
                    <tr key={inv.id}>
                      <td style={{ fontWeight: '600', color: 'var(--primary-blue)' }}>{inv.student_matric}</td>
                      <td>{inv.fee_type_name}</td>
                      <td style={{ fontWeight: '700' }}>₦{parseFloat(inv.amount).toLocaleString()}</td>
                      <td style={{ color: '#4ade80' }}>₦{parseFloat(inv.amount_paid).toLocaleString()}</td>
                      <td style={{ color: '#f87171' }}>₦{parseFloat(inv.balance).toLocaleString()}</td>
                      <td><span className="status-badge" style={{ backgroundColor: `${getStatusColor(inv.status)}20`, color: getStatusColor(inv.status), borderColor: `${getStatusColor(inv.status)}40` }}>{inv.status}</span></td>
                    </tr>
                  ))}
                  {activeTab === 'payments' && payments.map(pay => (
                    <tr key={pay.id}>
                      <td style={{ fontWeight: '600', color: 'var(--primary-blue)' }}>{pay.transaction_id}</td>
                      <td>{pay.student_matric}</td>
                      <td style={{ fontWeight: '700', color: '#1e40af' }}>₦{parseFloat(pay.amount).toLocaleString()}</td>
                      <td>{pay.payment_method}</td>
                      <td>{new Date(pay.payment_date).toLocaleDateString()}</td>
                      <td><span className="status-badge" style={{ backgroundColor: `${getStatusColor(pay.status)}20`, color: getStatusColor(pay.status), borderColor: `${getStatusColor(pay.status)}40` }}>{pay.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Finance;
