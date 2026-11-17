import { useState } from "react";

function PreprocessingPanel({
  filename,
  processedFilename,
  progress,
  onStartPreprocessing,
  onDownloadProcessed,
  onGenerateReport,
}) {
  const [outputFormat, setOutputFormat] = useState("csv");
  const [missingStrategy, setMissingStrategy] = useState("median");
  const [constantValue, setConstantValue] = useState("Unknown");
  const isProcessing = ["queued", "processing"].includes(progress?.status);
  const canDownload = Boolean(processedFilename && progress?.status === "completed");

  return (
    <section className="preprocessing-panel">
      <div className="preprocessing-header">
        <p className="section-label">DATA PREPROCESSING</p>
        <h2>Clean & Prepare Dataset</h2>
        <p>Trim text, remove duplicate rows, handle missing values, then export the processed dataset.</p>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <label className="grid gap-2 text-sm text-slate-300">
          Output format
          <select
            className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white"
            value={outputFormat}
            onChange={(event) => setOutputFormat(event.target.value)}
          >
            <option value="csv">CSV</option>
            <option value="pdf">PDF</option>
          </select>
        </label>

        <label className="grid gap-2 text-sm text-slate-300">
          Missing values
          <select
            className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white"
            value={missingStrategy}
            onChange={(event) => setMissingStrategy(event.target.value)}
          >
            <option value="median">Median / most common</option>
            <option value="mean">Mean / most common</option>
            <option value="mode">Most common value</option>
            <option value="constant">Constant value</option>
            <option value="drop_rows">Drop rows with missing values</option>
            <option value="drop_columns">Drop columns with missing values</option>
          </select>
        </label>
      </div>

      {missingStrategy === "constant" && (
        <label className="mt-4 grid gap-2 text-sm text-slate-300">
          Constant value
          <input
            className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white"
            value={constantValue}
            onChange={(event) => setConstantValue(event.target.value)}
          />
        </label>
      )}

      <div className="preprocessing-buttons">
        <button
          disabled={!filename || isProcessing}
          onClick={() =>
            onStartPreprocessing?.({
              output_format: outputFormat,
              missing_strategy: missingStrategy,
              constant_value: missingStrategy === "constant" ? constantValue : null,
            })
          }
        >
          {isProcessing ? "Processing..." : "Preprocess Dataset"}
        </button>
        <button disabled={!canDownload} onClick={onDownloadProcessed}>
          Download {processedFilename?.split(".").pop()?.toUpperCase() || outputFormat.toUpperCase()}
        </button>
        <button
          disabled={!canDownload}
          onClick={() => onGenerateReport?.("pdf")}
        >
          Download PDF Report
        </button>
      </div>

      <div
        className={`processing-status ${progress?.status === "failed" ? "border-red-500/30 bg-red-500/10 text-red-200" : ""}`}
        role="status"
      >
        {filename
          ? `${progress?.message || "Dataset is ready."} (${progress?.percent ?? 0}%)`
          : "Upload a file to begin preprocessing."}
      </div>
    </section>
  );
}

export default PreprocessingPanel;
