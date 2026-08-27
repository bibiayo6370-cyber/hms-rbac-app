import { useState } from "react";
import { apiClient } from "../api/client";
import { useApiList } from "../api/useApiList";
import { useAuth } from "../context/useAuth";
import { PageHeader, PrimaryButton, SecondaryButton, Card, FormField, inputClass, ErrorText, EmptyState } from "../components/ui";
import type { Patient, PatientFormInput } from "../types";

const CAN_REGISTER: string[] = ["SUPER_ADMIN", "ADMIN", "NURSE"];

const emptyForm: PatientFormInput = {
  first_name: "", last_name: "", date_of_birth: "", gender: "F",
  phone_number: "", email: "", address: "", next_of_kin_name: "", next_of_kin_phone: "",
};

export default function PatientsPage() {
  const { user } = useAuth();
  const canRegister = !!user && CAN_REGISTER.includes(user.role);
  const { items: patients, isLoading, error, reload } = useApiList<Patient>("/patients/patients/");

  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<PatientFormInput>(emptyForm);
  const [submitError, setSubmitError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const filtered = patients.filter((p) => {
    const q = search.toLowerCase();
    return (
      p.first_name.toLowerCase().includes(q) ||
      p.last_name.toLowerCase().includes(q) ||
      p.patient_number.toLowerCase().includes(q) ||
      p.phone_number.includes(q)
    );
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitError("");
    setSubmitting(true);
    try {
      await apiClient.post("/patients/patients/", form);
      setForm(emptyForm);
      setShowForm(false);
      reload();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: Record<string, string[]> } })?.response?.data;
      setSubmitError(detail ? Object.values(detail).flat().join(" ") : "Could not register patient.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <PageHeader
        title="Patient Registration"
        subtitle="Search existing patients or register a new one"
        action={canRegister && (
          <PrimaryButton onClick={() => setShowForm((s) => !s)}>
            {showForm ? "Cancel" : "+ New Patient"}
          </PrimaryButton>
        )}
      />

      {showForm && canRegister && (
        <Card className="mb-6">
          <h2 className="text-lg font-medium text-slate-800 mb-4">Register New Patient</h2>
          <ErrorText message={submitError} />
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6">
              <FormField label="First Name">
                <input required className={inputClass} value={form.first_name}
                  onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
              </FormField>
              <FormField label="Last Name">
                <input required className={inputClass} value={form.last_name}
                  onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
              </FormField>
              <FormField label="Date of Birth">
                <input required type="date" className={inputClass} value={form.date_of_birth}
                  onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })} />
              </FormField>
              <FormField label="Gender">
                <select className={inputClass} value={form.gender}
                  onChange={(e) => setForm({ ...form, gender: e.target.value as PatientFormInput["gender"] })}>
                  <option value="F">Female</option>
                  <option value="M">Male</option>
                  <option value="O">Other</option>
                </select>
              </FormField>
              <FormField label="Phone Number">
                <input className={inputClass} value={form.phone_number}
                  onChange={(e) => setForm({ ...form, phone_number: e.target.value })} />
              </FormField>
              <FormField label="Email">
                <input type="email" className={inputClass} value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })} />
              </FormField>
              <FormField label="Address">
                <input className={inputClass} value={form.address}
                  onChange={(e) => setForm({ ...form, address: e.target.value })} />
              </FormField>
              <FormField label="Next of Kin Name">
                <input className={inputClass} value={form.next_of_kin_name}
                  onChange={(e) => setForm({ ...form, next_of_kin_name: e.target.value })} />
              </FormField>
              <FormField label="Next of Kin Phone">
                <input className={inputClass} value={form.next_of_kin_phone}
                  onChange={(e) => setForm({ ...form, next_of_kin_phone: e.target.value })} />
              </FormField>
            </div>
            <div className="flex gap-3 mt-2">
              <PrimaryButton type="submit" disabled={submitting}>
                {submitting ? "Saving..." : "Register Patient"}
              </PrimaryButton>
              <SecondaryButton type="button" onClick={() => setShowForm(false)}>Cancel</SecondaryButton>
            </div>
          </form>
        </Card>
      )}

      <Card>
        <input
          className={`${inputClass} mb-4`}
          placeholder="Search by name, patient number, or phone..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {isLoading ? (
          <EmptyState message="Loading patients..." />
        ) : error ? (
          <ErrorText message={error} />
        ) : filtered.length === 0 ? (
          <EmptyState message="No patients found." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-200">
                  <th className="py-2 pr-4">Patient #</th>
                  <th className="py-2 pr-4">Name</th>
                  <th className="py-2 pr-4">Age</th>
                  <th className="py-2 pr-4">Gender</th>
                  <th className="py-2 pr-4">Phone</th>
                  <th className="py-2 pr-4">Registered</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((p) => (
                  <tr key={p.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-2 pr-4 font-medium text-teal-700">{p.patient_number}</td>
                    <td className="py-2 pr-4">{p.first_name} {p.last_name}</td>
                    <td className="py-2 pr-4">{p.age}</td>
                    <td className="py-2 pr-4">{p.gender}</td>
                    <td className="py-2 pr-4">{p.phone_number || "—"}</td>
                    <td className="py-2 pr-4 text-slate-500">{new Date(p.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
