function ReportPage() {
  return (
    <section className="space-y-6 rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-glass backdrop-blur-xl">
      <h1 className="text-3xl font-semibold text-white">Reports</h1>
      <p className="text-slate-300">
        Generate downloadable analytics reports for any processed dataset. Back-end support includes export to PDF, CSV, and HTML.
      </p>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl bg-slate-950 p-5 text-slate-300 shadow-sm">
          <h2 className="font-semibold text-white">Performance charts</h2>
          <p className="mt-2 text-sm text-slate-400">Track numerical summaries, scaling, and outlier detection in one place.</p>
        </div>
        <div className="rounded-2xl bg-slate-950 p-5 text-slate-300 shadow-sm">
          <h2 className="font-semibold text-white">Data export</h2>
          <p className="mt-2 text-sm text-slate-400">Download processed files and reports for reuse in BI tools or downstream analytics.</p>
        </div>
      </div>
    </section>
  );
}

export default ReportPage;
