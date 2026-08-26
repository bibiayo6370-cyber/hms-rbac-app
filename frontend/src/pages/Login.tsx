import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useAuth } from "../context/useAuth";

interface LoginForm { username: string; password: string; }

export default function Login() {
  const { register, handleSubmit } = useForm<LoginForm>();
  const { login, isLoading } = useAuth();
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function onSubmit(data: LoginForm) {
    setError("");
    try {
      await login(data.username, data.password);
      navigate("/dashboard");
    } catch {
      setError("Invalid username or password.");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
        <h1 className="text-xl font-semibold text-slate-800 mb-1">HIMS Login</h1>
        <p className="text-sm text-slate-500 mb-6">Hospital Information Management System</p>

        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

        <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
        <input {...register("username", { required: true })}
          className="w-full border border-slate-300 rounded px-3 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-teal-600" />

        <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
        <input type="password" {...register("password", { required: true })}
          className="w-full border border-slate-300 rounded px-3 py-2 mb-6 focus:outline-none focus:ring-2 focus:ring-teal-600" />

        <button type="submit" disabled={isLoading}
          className="w-full bg-teal-700 text-white py-2 rounded font-medium hover:bg-teal-800 disabled:opacity-50">
          {isLoading ? "Signing in..." : "Sign In"}
        </button>
      </form>
    </div>
  );
}
