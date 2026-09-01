import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../services/api";
import ErrorMessage from "../../components/ErrorMessage";
import Loading from "../../components/Loading";
import ImageUploader from "../../components/ImageUploader";

export default function EditProduct() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    name: "", description: "", price: "", stock: "", category_id: "", image_url: "", is_active: true,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [prodRes, catRes] = await Promise.all([
          api.get(`/products/${id}`),
          api.get("/categories"),
        ]);
        const p = prodRes.data;
        setForm({
          name: p.name, description: p.description || "",
          price: p.price.toString(), stock: p.stock.toString(),
          category_id: p.category_id, image_url: p.image_url || "",
          is_active: p.is_active,
        });
        setCategories(catRes.data.items || catRes.data);
      } catch (err) {
        setError(err.response?.data?.detail || "Product not found.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await api.patch(`/sellers/me/products/${id}`, {
        name: form.name,
        description: form.description,
        price: parseFloat(form.price),
        stock: parseInt(form.stock),
        category_id: form.category_id,
        image_url: form.image_url,
        is_active: form.is_active,
      });
      navigate("/seller/products");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update product.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Loading />;
  if (error && !form.name) return <div className="page"><div className="container"><ErrorMessage message={error} /></div></div>;

  return (
    <div className="page">
      <div className="container">
        <h1>Edit Product</h1>
        <form className="seller-form" onSubmit={handleSubmit}>
          {error && <ErrorMessage message={error} />}
          <div className="form-group">
            <label htmlFor="name">Product Name</label>
            <input type="text" id="name" name="name" value={form.name} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea id="description" name="description" rows="3" value={form.description} onChange={handleChange} />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="price">Price (৳)</label>
              <input type="number" id="price" name="price" step="0.01" min="0" value={form.price} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="stock">Stock</label>
              <input type="number" id="stock" name="stock" min="0" value={form.stock} onChange={handleChange} required />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="category_id">Category</label>
            <select id="category_id" name="category_id" value={form.category_id} onChange={handleChange} required>
              <option value="">Select category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Product image</label>
            <ImageUploader
              value={form.image_url}
              onChange={(url) => setForm({ ...form, image_url: url })}
              disabled={saving}
            />
            <div style={{ marginTop: 10 }}>
              <label htmlFor="image_url" style={{ fontSize: 13, color: "var(--gray-600)" }}>
                Or paste an image URL
              </label>
              <input
                type="text"
                id="image_url"
                name="image_url"
                value={form.image_url}
                onChange={handleChange}
                placeholder="https://example.com/product.jpg"
              />
            </div>
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} />
              Active (visible to customers)
            </label>
          </div>
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </form>
      </div>
    </div>
  );
}
