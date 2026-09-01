import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { userService } from "../../services/userService";
import { useToast } from "../../context/ToastContext";
import { Skeleton } from "../../components/dashboard/Skeleton";
import { IconUser, IconEdit } from "../../components/dashboard/Icon";

const validate = (values) => {
  const errs = {};
  if (!values.name || values.name.trim().length < 2) errs.name = "Name must be at least 2 characters.";
  if (values.phone && !/^[+()\-\d\s]{6,20}$/.test(values.phone)) errs.phone = "Enter a valid phone number.";
  return errs;
};

export default function Profile() {
  const { user, setUser } = useAuth();
  const toast = useToast();
  const [form, setForm] = useState(null);
  const [editing, setEditing] = useState(false);
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setForm({ name: user.name || "", phone: "" });
    }
  }, [user]);

  if (!form) {
    return (
      <div className="dash-page">
        <h1>Profile</h1>
        <div className="dash-card">
          <Skeleton height={20} width="40%" />
          <Skeleton height={16} style={{ marginTop: 12 }} />
        </div>
      </div>
    );
  }

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    if (errors[e.target.name]) setErrors({ ...errors, [e.target.name]: null });
  };

  const handleSave = async (e) => {
    e.preventDefault();
    const errs = validate(form);
    setErrors(errs);
    if (Object.keys(errs).length) return;
    setSaving(true);
    try {
      const updated = await userService.updateProfile({ name: form.name });
      setUser({ ...user, name: updated.name || form.name });
      toast.success("Profile updated.");
      setEditing(false);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  const initials = (user?.name || user?.email || "U")
    .split(/\s+/)
    .map((s) => s[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <div className="dash-page">
      <header className="dash-page-header">
        <div>
          <h1>Profile</h1>
          <p className="dash-muted">Manage your personal information.</p>
        </div>
        {!editing && (
          <button className="btn btn-outline" onClick={() => setEditing(true)}>
            <IconEdit size={14} /> Edit
          </button>
        )}
      </header>

      <section className="dash-card">
        <div className="dash-profile-header">
          <div className="dash-avatar dash-avatar-lg">{initials}</div>
          <div>
            <h2 className="dash-strong">{user?.name}</h2>
            <p className="dash-muted">{user?.email}</p>
            <span className="dash-status-pill" style={{ color: "var(--primary)", borderColor: "var(--primary)" }}>
              {user?.role}
            </span>
          </div>
        </div>

        <form className="dash-form" onSubmit={handleSave}>
          <div className="dash-form-row">
            <label>Full Name</label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              disabled={!editing}
              required
            />
            {errors.name && <span className="dash-field-error">{errors.name}</span>}
          </div>

          <div className="dash-form-row">
            <label>Email</label>
            <input type="email" value={user?.email || ""} disabled />
            <span className="dash-field-hint">Email cannot be changed. Contact support if needed.</span>
          </div>

          <div className="dash-form-row">
            <label>Phone</label>
            <input
              type="tel"
              name="phone"
              value={form.phone}
              onChange={handleChange}
              disabled={!editing}
              placeholder="+1 555 000 0000"
            />
            {errors.phone && <span className="dash-field-error">{errors.phone}</span>}
          </div>

          {editing && (
            <div className="dash-form-actions">
              <button type="button" className="btn btn-outline" onClick={() => { setEditing(false); setErrors({}); }}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? "Saving…" : "Save Changes"}
              </button>
            </div>
          )}
        </form>
      </section>
    </div>
  );
}
