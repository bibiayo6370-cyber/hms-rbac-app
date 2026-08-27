import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { inputClass } from "../components/ui";

export default function Login() {
  const { login, isLoading } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await login(username, password);
      navigate("/dashboard");
    } catch {
      setError("Invalid username or password.");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <form onSubmit={onSubmit} className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
        <h1 className="text-xl font-semibold text-slate-800 mb-1">HIMS Login</h1>
        <p className="text-sm text-slate-500 mb-6">Hospital Information Management System</p>

        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

        <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
        <input className={`${inputClass} mb-4`} value={username} onChange={(e) => setUsername(e.target.value)} />

        <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
        <input type="password" className={`${inputClass} mb-6`} value={password} onChange={(e) => setPassword(e.target.value)} />

        <button type="submit" disabled={isLoading}
          className="w-full bg-teal-700 text-white py-2 rounded font-medium hover:bg-teal-800 disabled:opacity-50">
          {isLoading ? "Signing in..." : "Sign In"}
        </button>
      </form>
    </div>
  );
}
