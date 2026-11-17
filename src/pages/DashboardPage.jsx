import { useCallback, useEffect, useState } from "react";
import DataStats from "../components/DataStats.jsx";
import DataTable from "../components/DataTable.jsx";
import FileUpload from "../components/FileUpload.jsx";
import PreprocessingPanel from "../components/PreprocessingPanel.jsx";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

function DashboardPage() {
  const [metadata, setMetadata] = useState(null);
  const [preview, setPreview] = useState([]);
  const [filename, setFilename] = useState("");
  const [processedFilename, setProcessedFilename] = useState("");
  const [progress, setProgress] = useState({ status: "idle", percent: 0, message: "Ready" });
  const [reportFilename, setReportFilename] = useState("");
  const [message, setMessage] = useState("");

  const fetchProgress = useCallback(async () => {
    if (!filename) return;

    try {
      const response = await fetch(`${API_BASE}/progress?filename=${encodeURIComponent(filename)}`);
      const data = await response.json();
      if (response.ok) {
        setProgress(data);
        if (data.status === "completed" && data.processed_filename) {
          setProcessedFilename(data.processed_filename);
          setMessage("Processing complete. Your file is ready to download.");
          const previewResponse = await fetch(
            `${API_BASE}/preview?filename=${encodeURIComponent(data.processed_filename)}&processed=true`,
          );
          const previewData = await previewResponse.json();
          if (!previewResponse.ok) {
            throw new Error(previewData.detail || "Could not load the processed preview.");
          }
          setPreview(previewData.preview || []);
        }
        if (data.status === "failed") {
          setMessage(data.message || "Preprocessing failed.");
        }
      }
    } catch (error) {
      console.error(error);
    }
  }, [filename]);

  useEffect(() => {
    if (!filename || !["queued", "processing"].includes(progress.status)) return undefined;

    const timer = setInterval(fetchProgress, 2000);
    return () => clearInterval(timer);
  }, [filename, progress.status, fetchProgress]);

  const handleMetadata = (metadata) => {
    if (!metadata?.filename) {
      setMetadata(null);
      setPreview([]);
      setFilename("");
      setProcessedFilename("");
      setProgress({ status: "idle", percent: 0, message: "Ready" });
      setReportFilename("");
      setMessage("");
      return;
    }

    setMetadata(metadata);
    setPreview(metadata.preview || []);
    setFilename(metadata.filename || "");
    setProcessedFilename("");
    setProgress({ status: "uploaded", percent: 0, message: "Dataset uploaded and ready." });
    setReportFilename("");
    setMessage("Dataset uploaded successfully.");
  };

  const handleStartPreprocessing = async (options) => {
    if (!filename) {
      setMessage("Upload a dataset before starting preprocessing.");
      return;
    }

    setMessage("Starting preprocessing...");
    setProgress({ status: "queued", percent: 5, message: "Preparing preprocessing task." });

    try {
      const response = await fetch(`${API_BASE}/preprocess`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...options, filename }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.message || "Preprocessing request failed.");
      }

      setProcessedFilename(data.processed_filename || "");
      setProgress({ status: "queued", percent: 5, message: data.message || "Queued for preprocessing." });
      setMessage("Preprocessing has been queued. Polling progress...");
    } catch (error) {
      console.error(error);
      setMessage(error.message || "Could not start preprocessing.");
      setProgress({ status: "failed", percent: 0, message: error.message || "Failed to start." });
    }
  };

  const handleDownloadProcessed = () => {
    if (!processedFilename) {
      setMessage("No processed file available to download.");
      return;
    }
    window.open(`${API_BASE}/download?filename=${encodeURIComponent(processedFilename)}`, "_blank");
  };

  const handleGenerateReport = async (type) => {
    if (!processedFilename) {
      setMessage("Please preprocess the dataset before generating a report.");
      return;
    }

    setMessage(`Generating ${type.toUpperCase()} report...`);

    try {
      const response = await fetch(`${API_BASE}/report?filename=${encodeURIComponent(processedFilename)}&report_type=${encodeURIComponent(type)}`, {
        method: "POST",
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.message || "Report generation failed.");
      }
      setReportFilename(data.report_filename || "");
      setMessage("Report generated successfully.");
      window.open(`${API_BASE}/download-report?report_filename=${encodeURIComponent(data.report_filename)}`, "_blank");
    } catch (error) {
      console.error(error);
      setMessage(error.message || "Report generation failed.");
    }
  };

  return (
    <section className="space-y-8">
      <header className="rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-glass backdrop-blur-xl">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300/80">Dashboard</p>
        <h1 className="mt-3 text-4xl font-semibold text-white">Data Processing Platform</h1>
        <p className="mt-4 max-w-2xl text-slate-300">
          Upload supported data files, preview their contents, clean them, and export the processed data as CSV or PDF.
        </p>
      </header>

      <div className="grid gap-6 xl:grid-cols-[minmax(360px,1fr)_minmax(420px,1fr)]">
        <div className="space-y-6">
          <FileUpload onMetadata={handleMetadata} onFilename={setFilename} />

          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
            <h2 className="text-2xl font-semibold text-white">Dataset Statistics</h2>
            <p className="mt-2 text-slate-300">Review dataset dimensions, missing values, duplicates, and current preprocessing status.</p>
            <div className="mt-6">
              <DataStats metadata={metadata} progress={progress} />
            </div>
          </div>
        </div>

        <PreprocessingPanel
          filename={filename}
          processedFilename={processedFilename}
          progress={progress}
          onStartPreprocessing={handleStartPreprocessing}
          onDownloadProcessed={handleDownloadProcessed}
          onGenerateReport={handleGenerateReport}
        />
      </div>

      <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold text-white">Preview</h2>
            <p className="mt-2 text-slate-300">View the first rows of your uploaded dataset before and after preprocessing.</p>
          </div>
          {message && <span className="text-sm text-cyan-300">{message}</span>}
        </div>

        <div className="mt-6 overflow-x-auto">
          <DataTable data={preview} />
        </div>
      </section>
    </section>
  );
}

export default DashboardPage;
