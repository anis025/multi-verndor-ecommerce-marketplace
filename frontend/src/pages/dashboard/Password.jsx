import { useState } from "react";
import { userService } from "../../services/userService";
import { useToast } from "../../context/ToastContext";
import { IconLock } from "../../components/dashboard/Icon";

const validate = ({ current_password, new_password, confirm }) => {
  const errs = {};
  if (!current_password) errs.current_password = "Current password is required.";
  if (!new_password || new_password.length < 6) errs.new_password = "New password must be at least 6 characters.";
  if (new_password !== confirm) errs.confirm = "Passwords do not match.";
  return errs;
};

export default function Password() {
  const toast = useToast();
  const [form, setForm] = useState({ current_password: "", new_password: "", confirm: "" });
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    if (errors[e.target.name]) setErrors({ ...errors, [e.target.name]: null });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate(form);
    setErrors(errs);
    if (Object.keys(errs).length) return;
    setSaving(true);
    try {
      await userService.changePassword({
        current_password: form.current_password,
        new_password: form.new_password,
      });
      toast.success("Password updated.");
      setForm({ current_password: "", new_password: "", confirm: "" });
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update password.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="dash-page">
      <header className="dash-page-header">
        <div>
          <h1>Password & Security</h1>
          <p className="dash-muted">Choose a strong password and keep it private.</p>
        </div>
      </header>

      <section className="dash-card">
        <form className="dash-form" onSubmit={handleSubmit} noValidate>
          <div className="dash-form-row">
            <label>Current Password</label>
            <input
              type="password"
              name="current_password"
              value={form.current_password}
              onChange={handleChange}
              required
              autoComplete="current-password"
            />
            {errors.current_password && <span className="dash-field-error">{errors.current_password}</span>}
          </div>
          <div className="dash-form-row">
            <label>New Password</label>
            <input
              type="password"
              name="new_password"
              value={form.new_password}
              onChange={handleChange}
              required
              minLength={6}
              autoComplete="new-password"
            />
            {errors.new_password && <span className="dash-field-error">{errors.new_password}</span>}
          </div>
          <div className="dash-form-row">
            <label>Confirm New Password</label>
            <input
              type="password"
              name="confirm"
              value={form.confirm}
              onChange={handleChange}
              required
              autoComplete="new-password"
            />
            {errors.confirm && <span className="dash-field-error">{errors.confirm}</span>}
          </div>
          <div className="dash-form-actions">
            <button type="submit" className="btn btn-primary" disabled={saving}>
              <IconLock size={14} /> {saving ? "Updating…" : "Update Password"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
