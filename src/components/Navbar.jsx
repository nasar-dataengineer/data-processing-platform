function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-title">
        <span className="logo-icon">📊</span>
        <div>
          <h1>DataFlow</h1>
          <p>Data Processing Dashboard</p>
        </div>
      </div>

      <div className="navbar-status">
        <span className="status-dot"></span>
        System Ready
      </div>
    </header>
  );
}

export default Navbar;
