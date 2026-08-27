export type Role =
  | "SUPER_ADMIN"
  | "ADMIN"
  | "DOCTOR"
  | "NURSE"
  | "LAB_TECH"
  | "PHARMACIST"
  | "BILLING_OFFICER";

export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  role_display: string;
  phone_number: string;
  department: string | null;
  is_active_staff: boolean;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface DashboardSummary {
  generated_at: string;
  patient_volume: {
    today: number;
    last_7_days_trend: { day: string; count: number; }[];
  };
  department_throughput_7_days: { department__name: string | null; count: number; }[];
  revenue: {
    today: number;
    last_7_days: number;
    outstanding_invoices: number;
  };
  laboratory: {
    pending_orders: number;
  };
}

// ---------- Module 1: Patients ----------
export interface Patient {
  id: string;
  patient_number: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  age: number;
  gender: "M" | "F" | "O";
  phone_number: string;
  email: string;
  address: string;
  next_of_kin_name: string;
  next_of_kin_phone: string;
  registered_by: string | null;
  registered_by_name: string | null;
  created_at: string;
  updated_at: string;
}

export type PatientFormInput = Omit<
  Patient,
  "id" | "patient_number" | "age" | "registered_by" | "registered_by_name" | "created_at" | "updated_at"
>;

// ---------- Module 2: Clinical (minimal, for encounter pickers in other modules) ----------
export interface Encounter {
  id: string;
  patient: string;
  provider: string | null;
  department: string | null;
  status: "OPEN" | "COMPLETED" | "CANCELLED";
  chief_complaint: string;
  started_at: string;
}

// ---------- Module 3: Laboratory ----------
export interface LaboratoryOrder {
  id: string;
  encounter: string;
  ordered_by: string | null;
  test_name: string;
  loinc_code: string;
  status: "ORDERED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";
  ordered_at: string;
  accepted_at: string | null;
}

export interface LaboratoryResult {
  id: string;
  order: string;
  performed_by: string | null;
  result_value: string;
  unit: string;
  reference_range: string;
  is_abnormal: boolean;
  notes: string;
  entered_at: string;
}

// ---------- Module 4: Pharmacy ----------
export interface Medication {
  id: string;
  name: string;
  strength: string;
  form: string;
  unit_price: string;
  stock_quantity: number;
}

export interface Prescription {
  id: string;
  encounter: string;
  medication: string;
  medication_name: string;
  prescribed_by: string | null;
  dosage_instructions: string;
  quantity: number;
  status: "PENDING" | "DISPENSED" | "CANCELLED";
  prescribed_at: string;
}

export interface DispensingRecord {
  id: string;
  prescription: string;
  dispensed_by: string | null;
  quantity_dispensed: number;
  dispensed_at: string;
  notes: string;
}

// ---------- Module 5: Billing ----------
export interface Payment {
  id: string;
  invoice: string;
  amount: string;
  method: "CASH" | "CARD" | "TRANSFER" | "INSURANCE";
  received_by: string | null;
  paid_at: string;
  reference: string;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  patient: string;
  encounter: string | null;
  consultation_fee: string;
  laboratory_charges: string;
  pharmacy_charges: string;
  other_charges: string;
  total_amount: string;
  amount_paid: string;
  balance_due: string;
  status: "UNPAID" | "PARTIALLY_PAID" | "PAID" | "VOID";
  created_by: string | null;
  created_at: string;
  payments: Payment[];
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
