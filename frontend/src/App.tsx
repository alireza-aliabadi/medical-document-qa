import { Link, Navigate, Route, Routes } from "react-router-dom";
import { getToken } from "./lib/api";
import ChatPage from "./pages/Chat";
import DashboardPage from "./pages/Dashboard";
import DocumentsPage from "./pages/Documents";
import LoginPage from "./pages/Login";
import PlatformPage from "./pages/Platform";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!getToken()) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <div className="min-h-screen">
      <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 py-4 flex gap-6">
        <span className="font-semibold text-teal-400">Medical KB</span>
        <Link to="/" className="hover:text-teal-300">Dashboard</Link>
        <Link to="/documents" className="hover:text-teal-300">Documents</Link>
        <Link to="/chat" className="hover:text-teal-300">Chat</Link>
        <Link to="/platform" className="hover:text-teal-300">Platform</Link>
      </nav>
      <main className="p-6 max-w-6xl mx-auto">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/documents" element={<ProtectedRoute><DocumentsPage /></ProtectedRoute>} />
          <Route path="/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
          <Route path="/platform" element={<ProtectedRoute><PlatformPage /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  );
}
