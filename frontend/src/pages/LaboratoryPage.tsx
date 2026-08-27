import { Fragment, useState } from "react";
import { apiClient } from "../api/client";
import { useApiList } from "../api/useApiList";
import { useAuth } from "../context/useAuth";
import { PageHeader, PrimaryButton, SecondaryButton, Card, Badge, FormField, inputClass, ErrorText, EmptyState } from "../components/ui";
import type { LaboratoryOrder, Encounter } from "../types";

const CAN_ORDER = ["SUPER_ADMIN", "DOCTOR", "NURSE"];
const CAN_RESULT = ["SUPER_ADMIN", "LAB_TECH"];

function statusTone(status: string) {
  if (status === "COMPLETED") return "green";
  if (status === "CANCELLED") return "red";
  return "amber";
}

export default function LaboratoryPage() {
  const { user } = useAuth();
  const canOrder = !!user && CAN_ORDER.includes(user.role);
  const canResult = !!user && CAN_RESULT.includes(user.role);

  const { items: orders, isLoading, error, reload } = useApiList<LaboratoryOrder>("/laboratory/orders/");
  const { items: encounters } = useApiList<Encounter>("/clinical/encounters/");

  const [showOrderForm, setShowOrderForm] = useState(false);
  const [orderForm, setOrderForm] = useState({ encounter: "", test_name: "", loinc_code: "" });
  const [orderError, setOrderError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [resultingOrderId, setResultingOrderId] = useState<string | null>(null);
  const [resultForm, setResultForm] = useState({ result_value: "", unit: "", reference_range: "", is_abnormal: false, notes: "" });
  const [resultError, setResultError] = useState("");

  async function submitOrder(e: React.FormEvent) {
    e.preventDefault();
    setOrderError("");
    setSubmitting(true);
    try {
      await apiClient.post("/laboratory/orders/", orderForm);
      setOrderForm({ encounter: "", test_name: "", loinc_code: "" });
      setShowOrderForm(false);
      reload();
    } catch {
      setOrderError("Could not create lab order. Check the fields and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  async function submitResult(orderId: string) {
    setResultError("");
    try {
      await apiClient.post("/laboratory/results/", { order: orderId, ...resultForm });
      setResultingOrderId(null);
      setResultForm({ result_value: "", unit: "", reference_range: "", is_abnormal: false, notes: "" });
      reload();
    } catch {
      setResultError("Could not save result. You may not have permission, or a result already exists for this order.");
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <PageHeader
        title="Laboratory"
        subtitle="Test orders and results"
        action={canOrder && (
          <PrimaryButton onClick={() => setShowOrderForm((s) => !s)}>
            {showOrderForm ? "Cancel" : "+ New Order"}
          </PrimaryButton>
        )}
      />

      {showOrderForm && canOrder && (
        <Card className="mb-6">
          <h2 className="text-lg font-medium text-slate-800 mb-4">New Laboratory Order</h2>
          <ErrorText message={orderError} />
          <form onSubmit={submitOrder}>
            <FormField label="Encounter">
              <select required className={inputClass} value={orderForm.encounter}
                onChange={(e) => setOrderForm({ ...orderForm, encounter: e.target.value })}>
                <option value="">Select an encounter...</option>
                {encounters.map((enc) => (
                  <option key={enc.id} value={enc.id}>
                    {enc.chief_complaint} — {new Date(enc.started_at).toLocaleDateString()}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField label="Test Name">
              <input required className={inputClass} value={orderForm.test_name}
                onChange={(e) => setOrderForm({ ...orderForm, test_name: e.target.value })}
                placeholder="e.g. Full Blood Count" />
            </FormField>
            <FormField label="LOINC Code (optional)">
              <input className={inputClass} value={orderForm.loinc_code}
                onChange={(e) => setOrderForm({ ...orderForm, loinc_code: e.target.value })} />
            </FormField>
            <div className="flex gap-3">
              <PrimaryButton type="submit" disabled={submitting}>{submitting ? "Saving..." : "Create Order"}</PrimaryButton>
              <SecondaryButton type="button" onClick={() => setShowOrderForm(false)}>Cancel</SecondaryButton>
            </div>
          </form>
        </Card>
      )}

      <Card>
        {isLoading ? (
          <EmptyState message="Loading lab orders..." />
        ) : error ? (
          <ErrorText message={error} />
        ) : orders.length === 0 ? (
          <EmptyState message="No laboratory orders yet." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-200">
                  <th className="py-2 pr-4">Test</th>
                  <th className="py-2 pr-4">Ordered</th>
                  <th className="py-2 pr-4">Status</th>
                  {canResult && <th className="py-2 pr-4">Action</th>}
                </tr>
              </thead>
              <tbody>
                {orders.map((o) => (
                  <Fragment key={o.id}>
                    <tr className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-2 pr-4 font-medium">{o.test_name}</td>
                      <td className="py-2 pr-4 text-slate-500">{new Date(o.ordered_at).toLocaleDateString()}</td>
                      <td className="py-2 pr-4"><Badge tone={statusTone(o.status)}>{o.status}</Badge></td>
                      {canResult && (
                        <td className="py-2 pr-4">
                          <button
                            className="text-teal-700 hover:underline text-sm font-medium"
                            onClick={() => setResultingOrderId(resultingOrderId === o.id ? null : o.id)}
                          >
                            {resultingOrderId === o.id ? "Cancel" : "Record Result"}
                          </button>
                        </td>
                      )}
                    </tr>
                    {resultingOrderId === o.id && (
                      <tr className="bg-slate-50">
                        <td colSpan={4} className="p-4">
                          <ErrorText message={resultError} />
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                            <input className={inputClass} placeholder="Result value" value={resultForm.result_value}
                              onChange={(e) => setResultForm({ ...resultForm, result_value: e.target.value })} />
                            <input className={inputClass} placeholder="Unit" value={resultForm.unit}
                              onChange={(e) => setResultForm({ ...resultForm, unit: e.target.value })} />
                            <input className={inputClass} placeholder="Reference range" value={resultForm.reference_range}
                              onChange={(e) => setResultForm({ ...resultForm, reference_range: e.target.value })} />
                            <label className="flex items-center gap-2 text-sm text-slate-700">
                              <input type="checkbox" checked={resultForm.is_abnormal}
                                onChange={(e) => setResultForm({ ...resultForm, is_abnormal: e.target.checked })} />
                              Abnormal
                            </label>
                          </div>
                          <PrimaryButton onClick={() => submitResult(o.id)}>Save Result</PrimaryButton>
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
