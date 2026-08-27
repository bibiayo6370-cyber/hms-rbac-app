import { Fragment, useState } from "react";
import { apiClient } from "../api/client";
import { useApiList } from "../api/useApiList";
import { useAuth } from "../context/useAuth";
import { PageHeader, PrimaryButton, SecondaryButton, Card, Badge, FormField, inputClass, ErrorText, EmptyState } from "../components/ui";
import type { Invoice, Patient } from "../types";

const CAN_MANAGE_BILLING = ["SUPER_ADMIN", "ADMIN", "BILLING_OFFICER"];

function statusTone(status: string) {
  if (status === "PAID") return "green";
  if (status === "PARTIALLY_PAID") return "amber";
  if (status === "VOID") return "red";
  return "slate";
}

const naira = (v: string | number) =>
  `\u20a6${Number(v).toLocaleString(undefined, { minimumFractionDigits: 2 })}`;

export default function BillingPage() {
  const { user } = useAuth();
  const canManage = !!user && CAN_MANAGE_BILLING.includes(user.role);

  const { items: invoices, isLoading, error, reload } = useApiList<Invoice>("/billing/invoices/");
  const { items: patients } = useApiList<Patient>("/patients/patients/");

  const [showInvoiceForm, setShowInvoiceForm] = useState(false);
  const [invoiceForm, setInvoiceForm] = useState({
    patient: "", consultation_fee: "2000.00", laboratory_charges: "0.00",
    pharmacy_charges: "0.00", other_charges: "0.00",
  });
  const [invoiceError, setInvoiceError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [payingInvoiceId, setPayingInvoiceId] = useState<string | null>(null);
  const [paymentForm, setPaymentForm] = useState({ amount: "", method: "CASH" as const, reference: "" });
  const [paymentError, setPaymentError] = useState("");

  async function submitInvoice(e: React.FormEvent) {
    e.preventDefault();
    setInvoiceError("");
    setSubmitting(true);
    try {
      await apiClient.post("/billing/invoices/", invoiceForm);
      setInvoiceForm({ patient: "", consultation_fee: "2000.00", laboratory_charges: "0.00", pharmacy_charges: "0.00", other_charges: "0.00" });
      setShowInvoiceForm(false);
      reload();
    } catch {
      setInvoiceError("Could not create invoice. Check the fields and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  async function submitPayment(invoiceId: string) {
    setPaymentError("");
    try {
      await apiClient.post("/billing/payments/", { invoice: invoiceId, ...paymentForm });
      setPayingInvoiceId(null);
      setPaymentForm({ amount: "", method: "CASH", reference: "" });
      reload();
    } catch {
      setPaymentError("Could not record payment. Check the amount and try again.");
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <PageHeader
        title="Billing & Payments"
        subtitle="Invoices and payment records"
        action={canManage && (
          <PrimaryButton onClick={() => setShowInvoiceForm((s) => !s)}>
            {showInvoiceForm ? "Cancel" : "+ New Invoice"}
          </PrimaryButton>
        )}
      />

      {showInvoiceForm && canManage && (
        <Card className="mb-6">
          <h2 className="text-lg font-medium text-slate-800 mb-4">New Invoice</h2>
          <ErrorText message={invoiceError} />
          <form onSubmit={submitInvoice}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6">
              <FormField label="Patient">
                <select required className={inputClass} value={invoiceForm.patient}
                  onChange={(e) => setInvoiceForm({ ...invoiceForm, patient: e.target.value })}>
                  <option value="">Select a patient...</option>
                  {patients.map((p) => (
                    <option key={p.id} value={p.id}>{p.patient_number} — {p.first_name} {p.last_name}</option>
                  ))}
                </select>
              </FormField>
              <FormField label="Consultation Fee (₦)">
                <input type="number" step="0.01" className={inputClass} value={invoiceForm.consultation_fee}
                  onChange={(e) => setInvoiceForm({ ...invoiceForm, consultation_fee: e.target.value })} />
              </FormField>
              <FormField label="Laboratory Charges (₦)">
                <input type="number" step="0.01" className={inputClass} value={invoiceForm.laboratory_charges}
                  onChange={(e) => setInvoiceForm({ ...invoiceForm, laboratory_charges: e.target.value })} />
              </FormField>
              <FormField label="Pharmacy Charges (₦)">
                <input type="number" step="0.01" className={inputClass} value={invoiceForm.pharmacy_charges}
                  onChange={(e) => setInvoiceForm({ ...invoiceForm, pharmacy_charges: e.target.value })} />
              </FormField>
              <FormField label="Other Charges (₦)">
                <input type="number" step="0.01" className={inputClass} value={invoiceForm.other_charges}
                  onChange={(e) => setInvoiceForm({ ...invoiceForm, other_charges: e.target.value })} />
              </FormField>
            </div>
            <div className="flex gap-3">
              <PrimaryButton type="submit" disabled={submitting}>{submitting ? "Saving..." : "Create Invoice"}</PrimaryButton>
              <SecondaryButton type="button" onClick={() => setShowInvoiceForm(false)}>Cancel</SecondaryButton>
            </div>
          </form>
        </Card>
      )}

      <Card>
        {isLoading ? (
          <EmptyState message="Loading invoices..." />
        ) : error ? (
          <ErrorText message={error} />
        ) : invoices.length === 0 ? (
          <EmptyState message="No invoices yet." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-200">
                  <th className="py-2 pr-4">Invoice #</th>
                  <th className="py-2 pr-4">Total</th>
                  <th className="py-2 pr-4">Paid</th>
                  <th className="py-2 pr-4">Balance</th>
                  <th className="py-2 pr-4">Status</th>
                  {canManage && <th className="py-2 pr-4">Action</th>}
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <Fragment key={inv.id}>
                    <tr className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-2 pr-4 font-medium text-teal-700">{inv.invoice_number}</td>
                      <td className="py-2 pr-4">{naira(inv.total_amount)}</td>
                      <td className="py-2 pr-4">{naira(inv.amount_paid)}</td>
                      <td className="py-2 pr-4 font-medium">{naira(inv.balance_due)}</td>
                      <td className="py-2 pr-4"><Badge tone={statusTone(inv.status)}>{inv.status.replace("_", " ")}</Badge></td>
                      {canManage && (
                        <td className="py-2 pr-4">
                          {inv.status !== "PAID" && inv.status !== "VOID" && (
                            <button
                              className="text-teal-700 hover:underline text-sm font-medium"
                              onClick={() => {
                                setPayingInvoiceId(payingInvoiceId === inv.id ? null : inv.id);
                                setPaymentForm({ amount: inv.balance_due, method: "CASH", reference: "" });
                              }}
                            >
                              {payingInvoiceId === inv.id ? "Cancel" : "Record Payment"}
                            </button>
                          )}
                        </td>
                      )}
                    </tr>
                    {payingInvoiceId === inv.id && (
                      <tr className="bg-slate-50">
                        <td colSpan={6} className="p-4">
                          <ErrorText message={paymentError} />
                          <div className="flex items-end gap-3 flex-wrap">
                            <FormField label="Amount (₦)">
                              <input type="number" step="0.01" className={inputClass} value={paymentForm.amount}
                                onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })} />
                            </FormField>
                            <FormField label="Method">
                              <select className={inputClass} value={paymentForm.method}
                                onChange={(e) => setPaymentForm({ ...paymentForm, method: e.target.value as typeof paymentForm.method })}>
                                <option value="CASH">Cash</option>
                                <option value="CARD">Card</option>
                                <option value="TRANSFER">Bank Transfer</option>
                              </select>
                            </FormField>
                            <FormField label="Reference (optional)">
                              <input className={inputClass} value={paymentForm.reference}
                                onChange={(e) => setPaymentForm({ ...paymentForm, reference: e.target.value })} />
                            </FormField>
                            <PrimaryButton onClick={() => submitPayment(inv.id)} className="mb-4">Confirm Payment</PrimaryButton>
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
