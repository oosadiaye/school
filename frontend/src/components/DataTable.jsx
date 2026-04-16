import { useState, useMemo } from 'react';
import { TableSkeleton } from './Skeleton';
import Pagination from './Pagination';
import { exportToCSV } from '../utils/export';

const SearchIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);

const DataTable = ({
  data,
  columns,
  loading,
  searchable = true,
  searchKeys = [],
  filterOptions = [],
  onFilterChange,
  onBulkDelete,
  onBulkExport,
  exportFilename = 'export',
  showPagination = true,
  pageSize: initialPageSize = 10,
  emptyMessage = 'No data available',
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});
  const [selectedRows, setSelectedRows] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);

  const filteredData = useMemo(() => {
    let result = [...data];
    
    if (searchTerm && searchKeys.length > 0) {
      const term = searchTerm.toLowerCase();
      result = result.filter(item => 
        searchKeys.some(key => {
          const value = key.split('.').reduce((obj, k) => obj?.[k], item);
          return value?.toString().toLowerCase().includes(term);
        })
      );
    }

    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        result = result.filter(item => {
          const itemValue = key.split('.').reduce((obj, k) => obj?.[k], item);
          return itemValue?.toString().toLowerCase() === value.toLowerCase();
        });
      }
    });

    return result;
  }, [data, searchTerm, searchKeys, filters]);

  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredData.slice(start, start + pageSize);
  }, [filteredData, currentPage, pageSize]);

  const totalPages = Math.ceil(filteredData.length / pageSize);

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedRows(paginatedData.map(item => item.id));
    } else {
      setSelectedRows([]);
    }
  };

  const handleSelectRow = (id) => {
    setSelectedRows(prev => 
      prev.includes(id) ? prev.filter(r => r !== id) : [...prev, id]
    );
  };

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
    setCurrentPage(1);
  };

  const handlePageChange = (page) => setCurrentPage(page);
  const handlePageSizeChange = (size) => {
    setPageSize(size);
    setCurrentPage(1);
  };

  const handleExport = () => {
    const exportColumns = columns.filter(col => col.key !== 'actions');
    exportToCSV(filteredData, exportFilename, exportColumns);
  };

  const handleBulkDelete = () => {
    if (window.confirm(`Are you sure you want to delete ${selectedRows.length} selected items?`)) {
      onBulkDelete?.(selectedRows);
      setSelectedRows([]);
    }
  };

  if (loading) {
    return (
      <div className="glass-card">
        <TableSkeleton rows={5} columns={columns.length} />
      </div>
    );
  }

  return (
    <div className="glass-card">
      <div className="table-toolbar">
        <div className="search-filter-group">
          {searchable && (
            <div className="search-input-wrapper">
              <SearchIcon />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
              />
            </div>
          )}
          {filterOptions.map(opt => (
            <select
              key={opt.key}
              className="filter-select"
              value={filters[opt.key] || ''}
              onChange={(e) => handleFilterChange(opt.key, e.target.value)}
            >
              <option value="">{opt.label}</option>
              {opt.options.map(opt2 => (
                <option key={opt2.value} value={opt2.value}>{opt2.label}</option>
              ))}
            </select>
          ))}
        </div>
        {onBulkExport && (
          <button className="bulk-btn bulk-btn-export" onClick={handleExport}>
            Export CSV
          </button>
        )}
      </div>

      {selectedRows.length > 0 && (
        <div className="bulk-actions-bar">
          <span className="bulk-count">{selectedRows.length} selected</span>
          <button className="bulk-btn bulk-btn-delete" onClick={handleBulkDelete}>
            Delete Selected
          </button>
        </div>
      )}

      <div className="table-container">
        <table className="glass-table">
          <thead>
            <tr>
              <th style={{ width: '40px' }}>
                <input
                  type="checkbox"
                  className="th-checkbox"
                  checked={selectedRows.length > 0 && selectedRows.length === paginatedData.length}
                  onChange={handleSelectAll}
                />
              </th>
              {columns.map(col => (
                <th key={col.key}>{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length + 1} style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              paginatedData.map((item, idx) => (
                <tr key={item.id || idx}>
                  <td>
                    <input
                      type="checkbox"
                      className="td-checkbox"
                      checked={selectedRows.includes(item.id)}
                      onChange={() => handleSelectRow(item.id)}
                    />
                  </td>
                  {columns.map(col => (
                    <td key={col.key}>
                      {col.render ? col.render(item) : col.key.split('.').reduce((obj, k) => obj?.[k], item)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showPagination && filteredData.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          pageSize={pageSize}
          totalItems={filteredData.length}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
        />
      )}
    </div>
  );
};

export default DataTable;
