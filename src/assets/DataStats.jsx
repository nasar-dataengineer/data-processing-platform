function DataStats({ data }) {
  const columns = data.length > 0 ? Object.keys(data[0]).length : 0;

  return (
    <div className="stats-grid">
      <div className="stat-card">
        <span>Rows</span>
        <strong>{data.length}</strong>
      </div>

      <div className="stat-card">
        <span>Columns</span>
        <strong>{columns}</strong>
      </div>

      <div className="stat-card">
        <span>Status</span>
        <strong className="success">Ready</strong>
      </div>
    </div>
  );
}


export default DataStats;