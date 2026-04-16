export const TableSkeleton = ({ rows = 5, columns = 5 }) => {
  return (
    <div style={{ padding: '1rem' }}>
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div key={rowIdx} style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', alignItems: 'center' }}>
          {Array.from({ length: columns }).map((_, colIdx) => (
            <div 
              key={colIdx} 
              className="skeleton" 
              style={{ 
                height: '1rem', 
                flex: colIdx === 0 ? 0.8 : 1,
                minWidth: colIdx === 0 ? '100px' : 'auto'
              }} 
            />
          ))}
        </div>
      ))}
    </div>
  );
};

export const CardSkeleton = () => {
  return (
    <div style={{ background: 'rgba(255,255,255,0.7)', borderRadius: '16px', padding: '1.5rem' }}>
      <div className="skeleton skeleton-title" />
      <div className="skeleton skeleton-text" style={{ width: '80%' }} />
      <div className="skeleton skeleton-text" style={{ width: '60%' }} />
    </div>
  );
};

export const StatCardSkeleton = () => {
  return (
    <div style={{ background: 'rgba(255,255,255,0.7)', borderRadius: '16px', padding: '1.25rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <div className="skeleton" style={{ width: '48px', height: '48px', borderRadius: '12px' }} />
      <div>
        <div className="skeleton skeleton-title" style={{ width: '60px', height: '24px' }} />
        <div className="skeleton skeleton-text" style={{ width: '80px' }} />
      </div>
    </div>
  );
};

export default TableSkeleton;
