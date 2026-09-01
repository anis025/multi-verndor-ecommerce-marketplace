import { useState, useEffect } from "react";
import api from "../../services/api";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";

export default function ManageCategories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [form, setForm] = useState({ name: "", description: "" });
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState(null);

  const fetchCategories = async () => {
    setLoading(true);
    try {
      const res = await api.get("/admin/categories", { params: { limit: 100 } });
      setCategories(res.data.items);
      setTotal(res.data.total);
    } catch {
      setCategories([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCategories(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      if (editingId) {
        await api.patch(`/admin/categories/${editingId}`, { name: form.name, description: form.description });
      } else {
        await api.post("/admin/categories", { name: form.name, description: form.description });
      }
      setForm({ name: "", description: "" });
      setEditingId(null);
      fetchCategories();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save category.");
    }
  };

  const handleEdit = (cat) => {
    setForm({ name: cat.name, description: cat.description || "" });
    setEditingId(cat.id);
  };

  const handleDelete = async (catId) => {
    if (!window.confirm("Delete this category?")) return;
    try {
      await api.delete(`/admin/categories/${catId}`);
      fetchCategories();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete.");
    }
  };

  const toggleActive = async (catId, isActive) => {
    await api.patch(`/admin/categories/${catId}`, { is_active: !isActive });
    fetchCategories();
  };

  return (
    <div className="page">
      <div className="container">
        <h1>Manage Categories</h1>
        <p className="subtitle">{total} categor{total !== 1 ? "ies" : "y"}</p>

        <form className="seller-form" onSubmit={handleSubmit} style={{ marginBottom: 24 }}>
          {error && <ErrorMessage message={error} />}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="name">Name</label>
              <input type="text" id="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div className="form-group">
              <label htmlFor="desc">Description</label>
              <input type="text" id="desc" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
          </div>
          <button className="btn btn-primary" type="submit">{editingId ? "Update" : "Add"} Category</button>
          {editingId && (
            <button className="btn btn-outline" type="button" style={{ marginLeft: 8 }} onClick={() => { setEditingId(null); setForm({ name: "", description: "" }); }}>
              Cancel
            </button>
          )}
        </form>

        {loading ? <Loading /> : (
          <div className="admin-table">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {categories.map((c) => (
                  <tr key={c.id}>
                    <td>{c.name}</td>
                    <td>{c.description || "—"}</td>
                    <td>
                      <span className={`badge ${c.is_active ? "badge-active" : "badge-inactive"}`}>
                        {c.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="actions-cell">
                      <button className="btn btn-outline btn-sm" onClick={() => handleEdit(c)}>Edit</button>
                      <button className="btn btn-outline btn-sm" onClick={() => toggleActive(c.id, c.is_active)}>
                        {c.is_active ? "Deactivate" : "Activate"}
                      </button>
                      <button className="btn btn-outline btn-sm btn-danger-text" onClick={() => handleDelete(c.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
