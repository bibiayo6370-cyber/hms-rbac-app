import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { apiClient } from "../api/client";
import { useAuth } from "../context/useAuth";
import type { DashboardSummary } from "../types";

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const { user, logout } = useAuth();

  useEffect(() => {
    apiClient.get<DashboardSummary>("/dashboard/summary/").then((res) => setData(res.data));
  }, []);

  if (!data) return <p className="p-8">Loading dashboard...</p>;

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-slate-800">Administrative Dashboard</h1>
          <p className="text-slate-500 text-sm">Welcome, {user?.first_name} ({user?.role_display})</p>
        </div>
        <button onClick={logout} className="text-sm text-slate-600 hover:text-red-600">Log out</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <MetricCard label="Patients Today" value={data.patient_volume.today} />
        <MetricCard label="Revenue Today" value={`₦${data.revenue.today.toLocaleString()}`} />
        <MetricCard label="Outstanding Invoices" value={data.revenue.outstanding_invoices} />
        <MetricCard label="Pending Lab Orders" value={data.laboratory.pending_orders} />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-slate-800 mb-4">Department Throughput (7 days)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data.department_throughput_7_days}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="department__name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#0f766e" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number; }) {
  return (
    <div className="bg-white rounded-lg shadow p-5">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="text-2xl font-semibold text-slate-800 mt-1">{value}</p>
    </div>
  );
}
