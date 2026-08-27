import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { useAuth } from "./context/useAuth";
import ProtectedRoute from "./components/ProtectedRoute";
import NavBar from "./components/NavBar";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import PatientsPage from "./pages/PatientsPage";
import LaboratoryPage from "./pages/LaboratoryPage";
import PharmacyPage from "./pages/PharmacyPage";
import BillingPage from "./pages/BillingPage";

function Layout({ children }: { children: React.ReactNode; }) {
  return (
    <>
      <NavBar />
      {children}
    </>
  );
}

function Unauthorized() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <p className="text-slate-600">You don't have permission to view this page.</p>
    </div>
  );
}

function RootRedirect() {
  const { user } = useAuth();
  return <Navigate to={user ? "/patients" : "/login"} replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/unauthorized" element={<Unauthorized />} />

          <Route path="/dashboard" element={
            <ProtectedRoute allowedRoles={["ADMIN", "SUPER_ADMIN"]}>
              <Layout><Dashboard /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/patients" element={
            <ProtectedRoute>
              <Layout><PatientsPage /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/laboratory" element={
            <ProtectedRoute>
              <Layout><LaboratoryPage /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/pharmacy" element={
            <ProtectedRoute>
              <Layout><PharmacyPage /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/billing" element={
            <ProtectedRoute>
              <Layout><BillingPage /></Layout>
            </ProtectedRoute>
          } />

          <Route path="/" element={<RootRedirect />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
