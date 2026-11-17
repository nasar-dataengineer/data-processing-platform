function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-title">MENU</div>

      <button className="sidebar-item active">
        📊 Dashboard
      </button>

      <button className="sidebar-item">
        📁 Data Files
      </button>

      <button className="sidebar-item">
        🔍 Analyze Data
      </button>

      <button className="sidebar-item">
        📈 Statistics
      </button>

      <button className="sidebar-item">
        ⚙️ Settings
      </button>
    </aside>
  );
}

export default Sidebar;