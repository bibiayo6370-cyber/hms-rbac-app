export type Role =
  | "SUPER_ADMIN" | "ADMIN" | "DOCTOR" | "NURSE"
  | "LAB_TECH" | "PHARMACIST" | "BILLING_OFFICER";

export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  role_display: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface DashboardSummary {
  generated_at: string;
  patient_volume: { today: number; last_7_days_trend: { day: string; count: number; }[]; };
  department_throughput_7_days: { department__name: string | null; count: number; }[];
  revenue: { today: number; last_7_days: number; outstanding_invoices: number; };
  laboratory: { pending_orders: number; };
}
