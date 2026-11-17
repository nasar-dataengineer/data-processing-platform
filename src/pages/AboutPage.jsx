function AboutPage() {
  return (
    <section className="space-y-6 rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-glass backdrop-blur-xl">
      <h1 className="text-3xl font-semibold text-white">About the Platform</h1>
      <p className="text-slate-300">
        This application combines modern frontend UI with a Python data processing backend. It is designed to upload, clean, analyze, and visualize structured datasets.
      </p>
      <ul className="space-y-3 text-slate-300">
        <li>• FastAPI backend with Pandas, Polars, Dask, and Scikit-learn.</li>
        <li>• React + Tailwind + Three.js for an immersive analytical experience.</li>
        <li>• Export processed results and generate detailed reports.</li>
      </ul>
    </section>
  );
}

export default AboutPage;
