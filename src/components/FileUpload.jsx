import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

function FileUpload({ onMetadata, onFilename }) {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [uploading, setUploading] = useState(false);

  const uploadFile = async () => {
    if (!file) {
      setMessage("Please select a file before uploading.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || result.message || "Upload failed");
      }

      setMessage(result.message || "Upload completed successfully.");
      onMetadata?.(result.metadata || {});
      onFilename?.(result.metadata?.filename || "");
    } catch (error) {
      console.error(error);
      setMessage(error.message || "Upload failed. Please try again.");
      onMetadata?.({});
      onFilename?.("");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-card rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
      <div className="upload-icon text-4xl">📂</div>
      <h2 className="mt-4 text-2xl font-semibold text-white">Upload Your Dataset</h2>
      <p className="mt-2 text-slate-300">
        Upload a CSV, Excel, JSON, Parquet, text, or selectable-text PDF file. Scanned PDFs need OCR and are not supported.
      </p>

      <label className="mt-6 inline-flex cursor-pointer rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400">
        Choose File
        <input
          type="file"
          accept=".csv,.xlsx,.xls,.json,.parquet,.txt,.pdf"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          hidden
        />
      </label>

      {file && (
        <div className="mt-4 space-y-3 rounded-2xl bg-slate-950/80 p-4 text-slate-200">
          <p>Selected file: <strong>{file.name}</strong></p>
          <button
            className="rounded-xl bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-slate-100"
            onClick={uploadFile}
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Upload Dataset"}
          </button>
        </div>
      )}

      {message && <p className="mt-4 text-sm text-slate-300">{message}</p>}
    </div>
  );
}

export default FileUpload;
