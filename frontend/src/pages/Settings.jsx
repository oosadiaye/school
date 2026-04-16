import { useState } from 'react';
import { useToast } from '../components/toast/ToastContext';

const Settings = () => {
  const toast = useToast();
  const [activeTab, setActiveTab] = useState('branding');
  const [saving, setSaving] = useState(false);
  
  const [branding, setBranding] = useState({
    schoolName: 'University Name',
    shortName: 'UNIVERSITY',
    tagline: 'Excellence in Education',
    address: '123 University Road, City, State',
    phone: '+234 800 123 4567',
    email: 'info@university.edu',
    website: 'www.university.edu',
    registrationNumber: 'REG/2024/001',
  });

  const [academic, setAcademic] = useState({
    currentSession: '2024/2025',
    currentSemester: 'First',
    sessionStartDate: '2024-09-01',
    sessionEndDate: '2025-06-30',
    registrationDeadline: '2024-10-15',
    examStartDate: '2025-04-01',
  });

  const [system, setSystem] = useState({
    timezone: 'Africa/Lagos',
    dateFormat: 'YYYY-MM-DD',
    currency: 'NGN',
    currencySymbol: '₦',
    maintenanceMode: false,
    registrationOpen: true,
  });

  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    smsNotifications: false,
    pushNotifications: true,
    admissionAlerts: true,
    paymentAlerts: true,
    academicAlerts: true,
  });

  const handleSave = async (section) => {
    setSaving(true);
    await new Promise(r => setTimeout(r, 1000));
    setSaving(false);
    toast.success(`${section} settings saved successfully!`);
  };

  const SectionIcon = ({ children }) => (
    <span style={{ marginRight: '0.5rem', opacity: 0.7 }}>{children}</span>
  );

  const InputField = ({ label, value, onChange, type = 'text', options = null }) => (
    <div className="form-group">
      <label className="glass-label">{label}</label>
      {options ? (
        <select className="glass-select" value={value} onChange={(e) => onChange(e.target.value)}>
          {options.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
        </select>
      ) : (
        <input className="glass-input" type={type} value={value} onChange={(e) => onChange(e.target.value)} />
      )}
    </div>
  );

  const Toggle = ({ checked, onChange, label }) => (
    <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: 'rgba(59, 130, 246, 0.05)', borderRadius: '12px', marginBottom: '0.75rem', cursor: 'pointer' }}>
      <span style={{ color: '#1e40af', fontWeight: 500 }}>{label}</span>
      <div style={{ position: 'relative', width: '48px', height: '26px' }}>
        <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} style={{ opacity: 0, width: 0, height: 0 }} />
        <div style={{ position: 'absolute', inset: 0, background: checked ? '#3b82f6' : '#cbd5e1', borderRadius: '13px', transition: '0.3s' }}>
          <div style={{ position: 'absolute', top: '3px', left: checked ? '25px' : '3px', width: '20px', height: '20px', background: 'white', borderRadius: '50%', transition: '0.3s', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }} />
        </div>
      </div>
    </label>
  );

  const tabs = [
    { id: 'branding', label: 'Branding', icon: '🎨' },
    { id: 'academic', label: 'Academic', icon: '📚' },
    { id: 'system', label: 'System', icon: '⚙️' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
  ];

  return (
    <div className="students-page">
      <div className="page-header">
        <h1 style={{ color: '#1e40af', fontWeight: 800, letterSpacing: '-0.03em', margin: 0, WebkitTextStroke: '1px rgba(59, 130, 246, 0.5)', textShadow: '2px 2px 0 rgba(59, 130, 246, 0.3)' }}>Settings</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', gap: '1.5rem' }}>
        <div className="glass-card" style={{ padding: '1rem', height: 'fit-content' }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                width: '100%',
                padding: '1rem',
                border: 'none',
                borderRadius: '10px',
                background: activeTab === tab.id ? 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)' : 'transparent',
                color: activeTab === tab.id ? 'white' : '#475569',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                marginBottom: '0.5rem',
                transition: 'all 0.2s',
                boxShadow: activeTab === tab.id ? '0 4px 15px rgba(59, 130, 246, 0.3)' : 'none',
              }}
            >
              <span style={{ marginRight: '0.75rem', fontSize: '1.1rem' }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        <div className="glass-card">
          {activeTab === 'branding' && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ margin: 0, color: '#1e40af', fontSize: '1.25rem' }}>Branding Settings</h2>
                <button
                  onClick={() => handleSave('Branding')}
                  disabled={saving}
                  style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', color: 'white', border: 'none', borderRadius: '10px', padding: '0.75rem 1.5rem', fontWeight: 600, cursor: saving ? 'not-allowed' : 'pointer', opacity: saving ? 0.7 : 1 }}
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
                <div style={{ gridColumn: '1 / -1', padding: '2rem', background: 'rgba(59, 130, 246, 0.05)', borderRadius: '16px', textAlign: 'center', border: '2px dashed rgba(59, 130, 246, 0.3)' }}>
                  <div style={{ width: '80px', height: '80px', background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', borderRadius: '16px', margin: '0 auto 1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', color: 'white', fontWeight: 800 }}>U</div>
                  <p style={{ color: '#64748b', fontSize: '0.9rem', margin: 0 }}>Click to upload logo (PNG, JPG, max 2MB)</p>
                </div>
                <InputField label="School Name" value={branding.schoolName} onChange={(v) => setBranding({ ...branding, schoolName: v })} />
                <InputField label="Short Name" value={branding.shortName} onChange={(v) => setBranding({ ...branding, shortName: v })} />
                <InputField label="Tagline" value={branding.tagline} onChange={(v) => setBranding({ ...branding, tagline: v })} />
                <InputField label="Address" value={branding.address} onChange={(v) => setBranding({ ...branding, address: v })} />
                <InputField label="Phone" value={branding.phone} onChange={(v) => setBranding({ ...branding, phone: v })} />
                <InputField label="Email" value={branding.email} onChange={(v) => setBranding({ ...branding, email: v })} type="email" />
                <InputField label="Website" value={branding.website} onChange={(v) => setBranding({ ...branding, website: v })} />
                <InputField label="Registration Number" value={branding.registrationNumber} onChange={(v) => setBranding({ ...branding, registrationNumber: v })} />
              </div>
            </>
          )}

          {activeTab === 'academic' && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ margin: 0, color: '#1e40af', fontSize: '1.25rem' }}>Academic Settings</h2>
                <button onClick={() => handleSave('Academic')} style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', color: 'white', border: 'none', borderRadius: '10px', padding: '0.75rem 1.5rem', fontWeight: 600, cursor: 'pointer' }}>Save Changes</button>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
                <InputField label="Current Session" value={academic.currentSession} onChange={(v) => setAcademic({ ...academic, currentSession: v })} />
                <InputField label="Current Semester" value={academic.currentSemester} onChange={(v) => setAcademic({ ...academic, currentSemester: v })} options={[{ value: 'First', label: 'First Semester' }, { value: 'Second', label: 'Second Semester' }]} />
                <InputField label="Session Start Date" value={academic.sessionStartDate} onChange={(v) => setAcademic({ ...academic, sessionStartDate: v })} type="date" />
                <InputField label="Session End Date" value={academic.sessionEndDate} onChange={(v) => setAcademic({ ...academic, sessionEndDate: v })} type="date" />
                <InputField label="Registration Deadline" value={academic.registrationDeadline} onChange={(v) => setAcademic({ ...academic, registrationDeadline: v })} type="date" />
                <InputField label="Exam Start Date" value={academic.examStartDate} onChange={(v) => setAcademic({ ...academic, examStartDate: v })} type="date" />
              </div>
            </>
          )}

          {activeTab === 'system' && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ margin: 0, color: '#1e40af', fontSize: '1.25rem' }}>System Settings</h2>
                <button onClick={() => handleSave('System')} style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', color: 'white', border: 'none', borderRadius: '10px', padding: '0.75rem 1.5rem', fontWeight: 600, cursor: 'pointer' }}>Save Changes</button>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
                <InputField label="Timezone" value={system.timezone} onChange={(v) => setSystem({ ...system, timezone: v })} options={[{ value: 'Africa/Lagos', label: 'Africa/Lagos (WAT)' }, { value: 'Africa/Lagos', label: 'UTC' }]} />
                <InputField label="Date Format" value={system.dateFormat} onChange={(v) => setSystem({ ...system, dateFormat: v })} options={[{ value: 'YYYY-MM-DD', label: 'YYYY-MM-DD' }, { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY' }, { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY' }]} />
                <InputField label="Currency" value={system.currency} onChange={(v) => setSystem({ ...system, currency: v })} options={[{ value: 'NGN', label: 'Nigerian Naira (NGN)' }, { value: 'USD', label: 'US Dollar (USD)' }]} />
                <InputField label="Currency Symbol" value={system.currencySymbol} onChange={(v) => setSystem({ ...system, currencySymbol: v })} />
              </div>
              <div style={{ marginTop: '1rem' }}>
                <Toggle checked={system.maintenanceMode} onChange={(v) => setSystem({ ...system, maintenanceMode: v })} label="Maintenance Mode" />
                <Toggle checked={system.registrationOpen} onChange={(v) => setSystem({ ...system, registrationOpen: v })} label="Student Registration Open" />
              </div>
            </>
          )}

          {activeTab === 'notifications' && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ margin: 0, color: '#1e40af', fontSize: '1.25rem' }}>Notification Settings</h2>
                <button onClick={() => handleSave('Notification')} style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', color: 'white', border: 'none', borderRadius: '10px', padding: '0.75rem 1.5rem', fontWeight: 600, cursor: 'pointer' }}>Save Changes</button>
              </div>
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ color: '#1e40af', fontSize: '1rem', marginBottom: '1rem' }}>Channels</h3>
                <Toggle checked={notifications.emailNotifications} onChange={(v) => setNotifications({ ...notifications, emailNotifications: v })} label="Email Notifications" />
                <Toggle checked={notifications.smsNotifications} onChange={(v) => setNotifications({ ...notifications, smsNotifications: v })} label="SMS Notifications" />
                <Toggle checked={notifications.pushNotifications} onChange={(v) => setNotifications({ ...notifications, pushNotifications: v })} label="Push Notifications" />
              </div>
              <div>
                <h3 style={{ color: '#1e40af', fontSize: '1rem', marginBottom: '1rem' }}>Alerts</h3>
                <Toggle checked={notifications.admissionAlerts} onChange={(v) => setNotifications({ ...notifications, admissionAlerts: v })} label="Admission Alerts" />
                <Toggle checked={notifications.paymentAlerts} onChange={(v) => setNotifications({ ...notifications, paymentAlerts: v })} label="Payment Alerts" />
                <Toggle checked={notifications.academicAlerts} onChange={(v) => setNotifications({ ...notifications, academicAlerts: v })} label="Academic Alerts" />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
