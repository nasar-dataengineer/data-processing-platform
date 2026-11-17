function DataStats({ metadata, progress }) {
  const rows = metadata?.rows ?? 0;
  const columns = metadata?.columns ?? 0;
  const duplicates = metadata?.duplicate_rows ?? 0;
  const missing = metadata?.missing_values
    ? Object.values(metadata.missing_values).reduce((sum, value) => sum + Number(value), 0)
    : 0;
  const status = progress?.status || "waiting";

  return (
    <div className="grid gap-4 md:grid-cols-4">
      <div className="stat-card">
        <span>Rows</span>
        <strong>{rows}</strong>
      </div>

      <div className="stat-card">
        <span>Columns</span>
        <strong>{columns}</strong>
      </div>

      <div className="stat-card">
        <span>Missing</span>
        <strong>{missing}</strong>
      </div>

      <div className="stat-card">
        <span>Status</span>
        <strong className={status === "completed" ? "success" : "text-slate-200"}>{status}</strong>
      </div>
    </div>
  );
}

export default DataStats;
