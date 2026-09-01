import { useState, useEffect } from "react";
import api from "../../services/api";
import Loading from "../../components/Loading";

export default function AdminSettings() {
  const [config, setConfig] = useState(null);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/admin/config")
      .then((res) => { setConfig(res.data); setForm(res.data); })
      .catch(() => setError("Failed to load configuration."))
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const handleToggle = (name) => setForm({ ...form, [name]: !form[name] });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true); setMessage(null); setError(null);
    try {
      const res = await api.put("/admin/config", form);
      setConfig(res.data); setForm(res.data);
      setMessage("Settings saved.");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save settings.");
    } finally { setSaving(false); }
  };

  if (loading) return <Loading />;

  return (
    <div className="page">
      <div className="container">
        <h1>System Settings</h1>
        <p className="subtitle">Global configuration</p>
        {message && (
          <div className="alert" style={{ background: "#dcfce7", color: "#166534", border: "1px solid #bbf7d0", padding: 12, borderRadius: 8 }}>
            {message}
          </div>
        )}
        {error && <div className="alert alert-error">{error}</div>}
        <form className="seller-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Site Name</label>
            <input type="text" name="site_name" value={form.site_name || ""} onChange={handleChange} />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Support Email</label>
              <input type="email" name="support_email" value={form.support_email || ""} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Currency</label>
              <input type="text" name="currency" value={form.currency || ""} onChange={handleChange} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Commission Rate (0-1)</label>
              <input type="number" step="0.01" min="0" max="1" name="commission_rate" value={form.commission_rate ?? 0} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Default Page Size</label>
              <input type="number" min="1" max="100" name="default_page_size" value={form.default_page_size ?? 20} onChange={handleChange} />
            </div>
          </div>
          <div className="form-group toggle-group">
            <label className="toggle-label">
              <input type="checkbox" checked={!!form.maintenance_mode} onChange={() => handleToggle("maintenance_mode")} /> Maintenance Mode
            </label>
            <label className="toggle-label">
              <input type="checkbox" checked={!!form.registration_open} onChange={() => handleToggle("registration_open")} /> Open Registration
            </label>
          </div>
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save Settings"}
          </button>
        </form>
      </div>
    </div>
  );
}
