import { Fragment, useState } from "react";
import { apiClient } from "../api/client";
import { useApiList } from "../api/useApiList";
import { useAuth } from "../context/useAuth";
import { PageHeader, PrimaryButton, SecondaryButton, Card, Badge, FormField, inputClass, ErrorText, EmptyState } from "../components/ui";
import type { Prescription, Medication, Encounter } from "../types";

const CAN_PRESCRIBE = ["SUPER_ADMIN", "DOCTOR", "NURSE"];
const CAN_DISPENSE = ["SUPER_ADMIN", "PHARMACIST"];

function statusTone(status: string) {
  if (status === "DISPENSED") return "green";
  if (status === "CANCELLED") return "red";
  return "amber";
}

export default function PharmacyPage() {
  const { user } = useAuth();
  const canPrescribe = !!user && CAN_PRESCRIBE.includes(user.role);
  const canDispense = !!user && CAN_DISPENSE.includes(user.role);

  const { items: prescriptions, isLoading, error, reload } = useApiList<Prescription>("/pharmacy/prescriptions/");
  const { items: medications } = useApiList<Medication>("/pharmacy/medications/");
  const { items: encounters } = useApiList<Encounter>("/clinical/encounters/");

  const [showRxForm, setShowRxForm] = useState(false);
  const [rxForm, setRxForm] = useState({ encounter: "", medication: "", dosage_instructions: "", quantity: 1 });
  const [rxError, setRxError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [dispensingId, setDispensingId] = useState<string | null>(null);
  const [dispenseQty, setDispenseQty] = useState(0);
  const [dispenseError, setDispenseError] = useState("");

  async function submitRx(e: React.FormEvent) {
    e.preventDefault();
    setRxError("");
    setSubmitting(true);
    try {
      await apiClient.post("/pharmacy/prescriptions/", rxForm);
      setRxForm({ encounter: "", medication: "", dosage_instructions: "", quantity: 1 });
      setShowRxForm(false);
      reload();
    } catch {
      setRxError("Could not save prescription. Check the fields and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  async function submitDispense(prescriptionId: string) {
    setDispenseError("");
    try {
      await apiClient.post("/pharmacy/dispensing-records/", {
        prescription: prescriptionId, quantity_dispensed: dispenseQty,
      });
      setDispensingId(null);
      reload();
    } catch {
      setDispenseError("Could not record dispensing. It may already be dispensed, or you lack permission.");
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <PageHeader
        title="Pharmacy"
        subtitle="Prescriptions and medication dispensing"
        action={canPrescribe && (
          <PrimaryButton onClick={() => setShowRxForm((s) => !s)}>
            {showRxForm ? "Cancel" : "+ New Prescription"}
          </PrimaryButton>
        )}
      />

      {showRxForm && canPrescribe && (
        <Card className="mb-6">
          <h2 className="text-lg font-medium text-slate-800 mb-4">New Prescription</h2>
          <ErrorText message={rxError} />
          <form onSubmit={submitRx}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6">
              <FormField label="Encounter">
                <select required className={inputClass} value={rxForm.encounter}
                  onChange={(e) => setRxForm({ ...rxForm, encounter: e.target.value })}>
                  <option value="">Select an encounter...</option>
                  {encounters.map((enc) => (
                    <option key={enc.id} value={enc.id}>
                      {enc.chief_complaint} — {new Date(enc.started_at).toLocaleDateString()}
                    </option>
                  ))}
                </select>
              </FormField>
              <FormField label="Medication">
                <select required className={inputClass} value={rxForm.medication}
                  onChange={(e) => setRxForm({ ...rxForm, medication: e.target.value })}>
                  <option value="">Select a medication...</option>
                  {medications.map((m) => (
                    <option key={m.id} value={m.id}>{m.name} {m.strength}</option>
                  ))}
                </select>
              </FormField>
              <FormField label="Dosage Instructions">
                <input required className={inputClass} value={rxForm.dosage_instructions}
                  onChange={(e) => setRxForm({ ...rxForm, dosage_instructions: e.target.value })}
                  placeholder="e.g. 1 tablet twice daily" />
              </FormField>
              <FormField label="Quantity">
                <input required type="number" min={1} className={inputClass} value={rxForm.quantity}
                  onChange={(e) => setRxForm({ ...rxForm, quantity: Number(e.target.value) })} />
              </FormField>
            </div>
            <div className="flex gap-3">
              <PrimaryButton type="submit" disabled={submitting}>{submitting ? "Saving..." : "Save Prescription"}</PrimaryButton>
              <SecondaryButton type="button" onClick={() => setShowRxForm(false)}>Cancel</SecondaryButton>
            </div>
          </form>
        </Card>
      )}

      <Card>
        {isLoading ? (
          <EmptyState message="Loading prescriptions..." />
        ) : error ? (
          <ErrorText message={error} />
        ) : prescriptions.length === 0 ? (
          <EmptyState message="No prescriptions yet." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-200">
                  <th className="py-2 pr-4">Medication</th>
                  <th className="py-2 pr-4">Dosage</th>
                  <th className="py-2 pr-4">Qty</th>
                  <th className="py-2 pr-4">Status</th>
                  {canDispense && <th className="py-2 pr-4">Action</th>}
                </tr>
              </thead>
              <tbody>
                {prescriptions.map((rx) => (
                  <Fragment key={rx.id}>
                    <tr className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-2 pr-4 font-medium">{rx.medication_name}</td>
                      <td className="py-2 pr-4">{rx.dosage_instructions}</td>
                      <td className="py-2 pr-4">{rx.quantity}</td>
                      <td className="py-2 pr-4"><Badge tone={statusTone(rx.status)}>{rx.status}</Badge></td>
                      {canDispense && (
                        <td className="py-2 pr-4">
                          {rx.status === "PENDING" && (
                            <button
                              className="text-teal-700 hover:underline text-sm font-medium"
                              onClick={() => {
                                setDispensingId(dispensingId === rx.id ? null : rx.id);
                                setDispenseQty(rx.quantity);
                              }}
                            >
                              {dispensingId === rx.id ? "Cancel" : "Dispense"}
                            </button>
                          )}
                        </td>
                      )}
                    </tr>
                    {dispensingId === rx.id && (
                      <tr className="bg-slate-50">
                        <td colSpan={5} className="p-4">
                          <ErrorText message={dispenseError} />
                          <div className="flex items-end gap-3">
                            <FormField label="Quantity to dispense">
                              <input type="number" min={1} max={rx.quantity} className={inputClass}
                                value={dispenseQty} onChange={(e) => setDispenseQty(Number(e.target.value))} />
                            </FormField>
                            <PrimaryButton onClick={() => submitDispense(rx.id)} className="mb-4">Confirm Dispense</PrimaryButton>
                          </div>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
