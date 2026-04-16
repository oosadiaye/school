export const exportToCSV = (data, filename, columns) => {
  if (!data || data.length === 0) return;

  const headers = columns.map(col => col.label).join(',');
  const rows = data.map(item => 
    columns.map(col => {
      let value = col.render ? col.render(item) : item[col.key];
      if (value === null || value === undefined) value = '';
      value = String(value).replace(/"/g, '""');
      return `"${value}"`;
    }).join(',')
  );

  const csv = [headers, ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
};

export const exportSelectedToCSV = (selectedItems, allData, filename, columns) => {
  const selectedData = allData.filter(item => selectedItems.includes(item.id));
  exportToCSV(selectedData, filename, columns);
};
