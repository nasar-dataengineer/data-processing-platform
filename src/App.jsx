import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import DashboardPage from "./pages/DashboardPage";
import AboutPage from "./pages/AboutPage";
import ReportPage from "./pages/ReportPage";
import SettingsPage from "./pages/SettingsPage";

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <div className="lg:flex lg:min-h-[calc(100vh-72px)]">
        <Sidebar />
        <main className="flex-1 px-4 py-6 lg:px-10 lg:py-8">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/reports" element={<ReportPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
