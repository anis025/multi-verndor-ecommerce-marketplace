import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import ErrorMessage from "../../components/ErrorMessage";
import ImageUploader from "../../components/ImageUploader";

const CUSTOM_CATEGORY_VALUE = "__custom__";

export default function AddProduct() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    name: "", description: "", price: "", stock: "", category_id: "", image_url: "",
  });
  const [customCategory, setCustomCategory] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/categories/active")
      .then((res) => setCategories(res.data.items || []))
      .catch(() => setCategories([]));
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const isCustom = form.category_id === CUSTOM_CATEGORY_VALUE;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!form.name.trim() || !form.price || !form.stock || !form.category_id) {
      setError("Name, price, stock, and category are required.");
      return;
    }

    setLoading(true);
    try {
      let categoryId = form.category_id;

      if (categoryId === CUSTOM_CATEGORY_VALUE) {
        if (!customCategory.trim()) {
          setError("Please enter a name for the new category.");
          setLoading(false);
          return;
        }
        const catRes = await api.post("/categories", {
          name: customCategory.trim(),
          is_active: true,
        });
        categoryId = catRes.data.id;
        setCategories((prev) => [...prev, catRes.data]);
      }

      await api.post("/sellers/me/products", {
        name: form.name,
        description: form.description,
        price: parseFloat(form.price),
        stock: parseInt(form.stock),
        category_id: categoryId,
        image_url: form.image_url,
      });
      navigate("/seller/products");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add product.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="container">
        <h1>Add Product</h1>
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
              <option value={CUSTOM_CATEGORY_VALUE}>+ Add custom category…</option>
            </select>
          </div>

          {isCustom && (
            <div className="form-group">
              <label htmlFor="customCategory">New Category Name</label>
              <input
                type="text"
                id="customCategory"
                name="customCategory"
                value={customCategory}
                onChange={(e) => setCustomCategory(e.target.value)}
                placeholder="e.g., Vintage Hats"
                required
              />
            </div>
          )}

          <div className="form-group">
            <label>Product image</label>
            <ImageUploader
              value={form.image_url}
              onChange={(url) => setForm({ ...form, image_url: url })}
              disabled={loading}
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

          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Adding..." : "Add Product"}
          </button>
        </form>
      </div>
    </div>
  );
}
