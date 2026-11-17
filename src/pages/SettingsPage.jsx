function SettingsPage() {
  return (
    <section className="space-y-6 rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-glass backdrop-blur-xl">
      <h1 className="text-3xl font-semibold text-white">Settings</h1>
      <p className="text-slate-300">
        Configure file handling, processing preferences, and visualization defaults for your data workflows.
      </p>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl bg-slate-950 p-5 text-slate-300 shadow-sm">
          <h2 className="font-semibold text-white">Upload options</h2>
          <p className="mt-2 text-sm text-slate-400">Choose file types and preview limits.</p>
        </div>
        <div className="rounded-2xl bg-slate-950 p-5 text-slate-300 shadow-sm">
          <h2 className="font-semibold text-white">Processing rules</h2>
          <p className="mt-2 text-sm text-slate-400">Select preprocessing strategies such as scaling, encoding, and outlier removal.</p>
        </div>
      </div>
    </section>
  );
}

export default SettingsPage;
