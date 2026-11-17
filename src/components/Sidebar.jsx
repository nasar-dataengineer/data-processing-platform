import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside className="w-full max-w-[260px] space-y-4 rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-glass backdrop-blur-xl lg:sticky lg:top-0 lg:self-start">
      <div className="mb-8 text-slate-300">
        <p className="text-xs uppercase tracking-[0.3em] text-cyan-300/70">Workspace</p>
        <h2 className="mt-3 text-2xl font-semibold text-white">Navigation</h2>
      </div>
      <nav className="space-y-2">
        {[
          { to: "/", label: "📊 Dashboard" },
          { to: "/reports", label: "📈 Reports" },
          { to: "/about", label: "ℹ️ About" },
          { to: "/settings", label: "⚙️ Settings" },
        ].map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `block rounded-2xl px-4 py-3 text-sm font-medium transition ${
                isActive ? "bg-cyan-500/15 text-cyan-200" : "text-slate-300 hover:bg-slate-800/80 hover:text-white"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;
