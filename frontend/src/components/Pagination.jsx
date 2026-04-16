const Pagination = ({ currentPage, totalPages, pageSize, totalItems, onPageChange, onPageSizeChange }) => {
  const pageSizeOptions = [10, 25, 50, 100];
  const maxVisiblePages = 5;
  
  const getVisiblePages = () => {
    let start = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let end = Math.min(totalPages, start + maxVisiblePages - 1);
    if (end - start + 1 < maxVisiblePages) {
      start = Math.max(1, end - maxVisiblePages + 1);
    }
    const pages = [];
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  };

  if (totalPages <= 1) return null;

  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalItems);

  return (
    <div className="pagination">
      <div className="pagination-info">
        Showing {startItem} to {endItem} of {totalItems} entries
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <select 
          className="page-size-select" 
          value={pageSize} 
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
        >
          {pageSizeOptions.map(size => (
            <option key={size} value={size}>{size} per page</option>
          ))}
        </select>
        <div className="pagination-controls">
          <button 
            className="pagination-btn" 
            onClick={() => onPageChange(1)}
            disabled={currentPage === 1}
          >
            ««
          </button>
          <button 
            className="pagination-btn" 
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            «
          </button>
          {getVisiblePages().map(page => (
            <button
              key={page}
              className={`pagination-btn ${page === currentPage ? 'active' : ''}`}
              onClick={() => onPageChange(page)}
            >
              {page}
            </button>
          ))}
          <button 
            className="pagination-btn" 
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            »
          </button>
          <button 
            className="pagination-btn" 
            onClick={() => onPageChange(totalPages)}
            disabled={currentPage === totalPages}
          >
            »»
          </button>
        </div>
      </div>
    </div>
  );
};

export default Pagination;
