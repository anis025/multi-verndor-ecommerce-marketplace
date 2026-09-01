import { useEffect, useState } from "react";
import { paymentService } from "../../services/paymentService";
import { useToast } from "../../context/ToastContext";
import { Skeleton } from "../../components/dashboard/Skeleton";
import EmptyState from "../../components/dashboard/EmptyState";
import ConfirmDialog from "../../components/dashboard/ConfirmDialog";
import { IconCard, IconPlus, IconTrash, IconCheck } from "../../components/dashboard/Icon";

// UI-only: collects masked display fields. The service is structured to accept
// a real provider token in the future without UI refactors.
export default function Payments() {
  const toast = useToast();
  const [items, setItems] = useState(null);
  const [adding, setAdding] = useState(false);
  const [confirm, setConfirm] = useState(null);
  const [form, setForm] = useState({ brand: "Visa", last4: "", exp_month: "", exp_year: "", holder_name: "", is_default: false });

  useEffect(() => {
    paymentService.list().then(setItems).catch(() => setItems([]));
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!/^\d{4}$/.test(form.last4)) {
      toast.error("Enter the last 4 digits only.");
      return;
    }
    const m = Number(form.exp_month), y = Number(form.exp_year);
    if (!(m >= 1 && m <= 12) || !(y >= 2025 && y <= 2099)) {
      toast.error("Enter a valid expiry month/year.");
      return;
    }
    try {
      const created = await paymentService.add(form);
      setItems((arr) => [...arr, created]);
      toast.success("Card added.");
      setAdding(false);
      setForm({ brand: "Visa", last4: "", exp_month: "", exp_year: "", holder_name: "", is_default: false });
    } catch {
      toast.error("Failed to add card.");
    }
  };

  const handleDelete = async () => {
    const id = confirm;
    setConfirm(null);
    try {
      await paymentService.remove(id);
      setItems((arr) => arr.filter((p) => p.id !== id));
      toast.success("Card removed.");
    } catch {
      toast.error("Failed to remove card.");
    }
  };

  const handleSetDefault = async (id) => {
    try {
      await paymentService.setDefault(id);
      setItems((arr) => arr.map((p) => ({ ...p, is_default: p.id === id })));
      toast.success("Default card updated.");
    } catch {
      toast.error("Failed to update default.");
    }
  };

  if (items === null) {
    return (
      <div className="dash-page">
        <h1>Payment Methods</h1>
        <div className="dash-grid-cards">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="dash-card"><Skeleton height={20} width="50%" /></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="dash-page">
      <header className="dash-page-header">
        <div>
          <h1>Payment Methods</h1>
          <p className="dash-muted">Manage your saved cards. Demo data only — no real payment info is stored.</p>
        </div>
        {!adding && (
          <button className="btn btn-primary" onClick={() => setAdding(true)}>
            <IconPlus size={14} /> Add Card
          </button>
        )}
      </header>

      {adding && (
        <section className="dash-card">
          <h2 className="dash-section-title">Add Card (Demo)</h2>
          <div className="dash-callout">
            <IconCard size={18} />
            <p>
              For this demo we only store masked last 4 digits and the cardholder name.
              In production, integrate a PCI-compliant provider (Stripe Elements, Braintree, etc.)
              to tokenize cards — this form's <code>paymentService.add()</code> signature is the
              single integration point.
            </p>
          </div>
          <form className="dash-form" onSubmit={handleAdd}>
            <div className="dash-form-grid">
              <div>
                <label>Brand</label>
                <select name="brand" value={form.brand} onChange={(e) => setForm({ ...form, brand: e.target.value })}>
                  <option>Visa</option>
                  <option>Mastercard</option>
                  <option>Amex</option>
                  <option>Discover</option>
                </select>
              </div>
              <div>
                <label>Last 4 Digits</label>
                <input
                  inputMode="numeric"
                  maxLength={4}
                  value={form.last4}
                  onChange={(e) => setForm({ ...form, last4: e.target.value.replace(/\D/g, "") })}
                  required
                />
              </div>
            </div>
            <div className="dash-form-grid">
              <div>
                <label>Expiry Month</label>
                <input
                  type="number" min={1} max={12}
                  value={form.exp_month}
                  onChange={(e) => setForm({ ...form, exp_month: e.target.value })}
                  required
                />
              </div>
              <div>
                <label>Expiry Year</label>
                <input
                  type="number" min={2025} max={2099}
                  value={form.exp_year}
                  onChange={(e) => setForm({ ...form, exp_year: e.target.value })}
                  required
                />
              </div>
            </div>
            <div className="dash-form-row">
              <label>Cardholder Name</label>
              <input
                value={form.holder_name}
                onChange={(e) => setForm({ ...form, holder_name: e.target.value })}
                required
              />
            </div>
            <div className="dash-form-row">
              <label className="dash-check">
                <input
                  type="checkbox"
                  checked={form.is_default}
                  onChange={(e) => setForm({ ...form, is_default: e.target.checked })}
                />
                <span>Set as default</span>
              </label>
            </div>
            <div className="dash-form-actions">
              <button type="button" className="btn btn-outline" onClick={() => setAdding(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary">Save Card</button>
            </div>
          </form>
        </section>
      )}

      {items.length === 0 && !adding ? (
        <EmptyState
          icon={IconCard}
          title="No payment methods"
          description="Add a card to make checkout faster."
          actionLabel="Add Card"
          onAction={() => setAdding(true)}
        />
      ) : (
        <div className="dash-grid-cards">
          {items.map((p) => (
            <article key={p.id} className="dash-card dash-payment-card">
              <div className="dash-payment-head">
                <div className="dash-payment-brand">{p.brand}</div>
                {p.is_default && <span className="dash-badge-default">Default</span>}
              </div>
              <div className="dash-payment-number">•••• •••• •••• {p.last4}</div>
              <div className="dash-muted">Expires {String(p.exp_month).padStart(2, "0")}/{String(p.exp_year).slice(-2)}</div>
              <div className="dash-muted">{p.holder_name}</div>
              <div className="dash-payment-actions">
                {!p.is_default && (
                  <button className="btn btn-outline btn-sm" onClick={() => handleSetDefault(p.id)}>
                    <IconCheck size={14} /> Set Default
                  </button>
                )}
                <button className="btn btn-outline btn-sm" onClick={() => setConfirm(p.id)}>
                  <IconTrash size={14} /> Remove
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={!!confirm}
        title="Remove this card?"
        message="The card will be removed from your saved methods."
        confirmLabel="Remove"
        onConfirm={handleDelete}
        onCancel={() => setConfirm(null)}
      />
    </div>
  );
}
