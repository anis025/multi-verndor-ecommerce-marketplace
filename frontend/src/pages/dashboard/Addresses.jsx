import { useEffect, useState } from "react";
import { addressService } from "../../services/addressService";
import { useToast } from "../../context/ToastContext";
import { Skeleton } from "../../components/dashboard/Skeleton";
import EmptyState from "../../components/dashboard/EmptyState";
import ConfirmDialog from "../../components/dashboard/ConfirmDialog";
import { IconMapPin, IconPlus, IconTrash, IconEdit } from "../../components/dashboard/Icon";

const empty = () => ({
  label: "Home",
  name: "",
  phone: "",
  line1: "",
  line2: "",
  city: "",
  state: "",
  postal_code: "",
  country: "",
  is_default: false,
});

const validate = (a) => {
  const e = {};
  if (!a.name) e.name = "Name is required.";
  if (!a.phone || a.phone.replace(/\D/g, "").length < 6) e.phone = "Enter a valid phone.";
  if (!a.line1) e.line1 = "Street address is required.";
  if (!a.city) e.city = "City is required.";
  if (!a.postal_code) e.postal_code = "Postal code is required.";
  if (!a.country) e.country = "Country is required.";
  return e;
};

export default function Addresses() {
  const toast = useToast();
  const [items, setItems] = useState(null);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(null);
  const [confirm, setConfirm] = useState(null);
  const [form, setForm] = useState(empty());
  const [errors, setErrors] = useState({});

  useEffect(() => {
    setError(null);
    addressService
      .list()
      .then(setItems)
      .catch(() => {
        setError("Could not load addresses.");
        setItems([]);
      });
  }, []);

  const startNew = () => {
    setForm(empty());
    setErrors({});
    setEditing("new");
  };

  const startEdit = (a) => {
    setForm({ ...a });
    setErrors({});
    setEditing(a.id);
  };

  const handleChange = (e) => {
    const { name, type, value, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
    if (errors[name]) setErrors({ ...errors, [name]: null });
  };

  const handleSave = async (e) => {
    e.preventDefault();
    const errs = validate(form);
    setErrors(errs);
    if (Object.keys(errs).length) return;
    try {
      if (editing === "new") {
        const created = await addressService.create(form);
        setItems((arr) => [...arr, created]);
        toast.success("Address added.");
      } else {
        const updated = await addressService.update(editing, form);
        setItems((arr) => arr.map((a) => (a.id === editing ? updated : a)));
        toast.success("Address updated.");
      }
      setEditing(null);
    } catch {
      toast.error("Failed to save address.");
    }
  };

  const handleDelete = async () => {
    const id = confirm;
    setConfirm(null);
    try {
      await addressService.remove(id);
      setItems((arr) => arr.filter((a) => a.id !== id));
      toast.success("Address deleted.");
    } catch {
      toast.error("Failed to delete address.");
    }
  };

  if (items === null) {
    return (
      <div className="dash-page">
        <h1>Address Book</h1>
        <div className="dash-grid-cards">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="dash-card">
              <Skeleton height={16} width="40%" style={{ marginBottom: 12 }} />
              <Skeleton height={14} style={{ marginBottom: 6 }} />
              <Skeleton height={14} style={{ marginBottom: 6 }} />
              <Skeleton height={14} width="70%" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="dash-page">
      <header className="dash-page-header">
        <div>
          <h1>Address Book</h1>
          <p className="dash-muted">{items.length} address{items.length !== 1 ? "es" : ""} saved.</p>
        </div>
        {!editing && (
          <button className="btn btn-primary" onClick={startNew}>
            <IconPlus size={14} /> Add New Address
          </button>
        )}
      </header>

      {error && <div className="alert alert-error">{error}</div>}

      {editing && (
        <section className="dash-card">
          <h2 className="dash-section-title">{editing === "new" ? "Add Address" : "Edit Address"}</h2>
          <form className="dash-form" onSubmit={handleSave}>
            <div className="dash-form-row">
              <label>Label</label>
              <select name="label" value={form.label} onChange={handleChange}>
                <option>Home</option>
                <option>Office</option>
                <option>Other</option>
              </select>
            </div>
            <div className="dash-form-grid">
              <div>
                <label>Full Name</label>
                <input name="name" value={form.name} onChange={handleChange} required />
                {errors.name && <span className="dash-field-error">{errors.name}</span>}
              </div>
              <div>
                <label>Phone</label>
                <input name="phone" value={form.phone} onChange={handleChange} required />
                {errors.phone && <span className="dash-field-error">{errors.phone}</span>}
              </div>
            </div>
            <div className="dash-form-row">
              <label>Address Line 1</label>
              <input name="line1" value={form.line1} onChange={handleChange} required />
              {errors.line1 && <span className="dash-field-error">{errors.line1}</span>}
            </div>
            <div className="dash-form-row">
              <label>Address Line 2</label>
              <input name="line2" value={form.line2} onChange={handleChange} />
            </div>
            <div className="dash-form-grid">
              <div>
                <label>City</label>
                <input name="city" value={form.city} onChange={handleChange} required />
                {errors.city && <span className="dash-field-error">{errors.city}</span>}
              </div>
              <div>
                <label>State / Region</label>
                <input name="state" value={form.state} onChange={handleChange} />
              </div>
            </div>
            <div className="dash-form-grid">
              <div>
                <label>Postal Code</label>
                <input name="postal_code" value={form.postal_code} onChange={handleChange} required />
                {errors.postal_code && <span className="dash-field-error">{errors.postal_code}</span>}
              </div>
              <div>
                <label>Country</label>
                <input name="country" value={form.country} onChange={handleChange} required />
                {errors.country && <span className="dash-field-error">{errors.country}</span>}
              </div>
            </div>
            <div className="dash-form-row">
              <label className="dash-check">
                <input type="checkbox" name="is_default" checked={form.is_default} onChange={handleChange} />
                <span>Set as default address</span>
              </label>
            </div>
            <div className="dash-form-actions">
              <button type="button" className="btn btn-outline" onClick={() => setEditing(null)}>Cancel</button>
              <button type="submit" className="btn btn-primary">Save Address</button>
            </div>
          </form>
        </section>
      )}

      {!editing && (items.length === 0 ? (
        <EmptyState
          icon={IconMapPin}
          title="No addresses saved"
          description="Add an address to make checkout faster."
          actionLabel="Add Address"
          onAction={startNew}
        />
      ) : (
        <div className="dash-grid-cards">
          {items.map((a) => (
            <article key={a.id} className="dash-card dash-address-card">
              <div className="dash-address-head">
                <div>
                  <span className="dash-address-label">{a.label}</span>
                  {a.is_default && <span className="dash-badge-default">Default</span>}
                </div>
                <div className="dash-address-actions">
                  <button className="btn btn-outline btn-sm" onClick={() => startEdit(a)}>
                    <IconEdit size={14} /> Edit
                  </button>
                  <button className="btn btn-outline btn-sm" onClick={() => setConfirm(a.id)}>
                    <IconTrash size={14} /> Delete
                  </button>
                </div>
              </div>
              <div className="dash-strong">{a.name}</div>
              <div className="dash-muted">{a.phone}</div>
              <div className="dash-muted">
                {a.line1}{a.line2 ? `, ${a.line2}` : ""}<br />
                {a.city}{a.state ? `, ${a.state}` : ""} {a.postal_code}<br />
                {a.country}
              </div>
            </article>
          ))}
        </div>
      ))}

      <ConfirmDialog
        open={!!confirm}
        title="Delete this address?"
        message="This address will be removed from your account."
        confirmLabel="Delete"
        onConfirm={handleDelete}
        onCancel={() => setConfirm(null)}
      />
    </div>
  );
}
