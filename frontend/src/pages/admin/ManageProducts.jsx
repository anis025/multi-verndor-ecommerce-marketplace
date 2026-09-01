import { useState, useEffect } from "react";
import api from "../../services/api";
import Loading from "../../components/Loading";

export default function ManageProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const fetchProducts = async (p) => {
    setLoading(true);
    try {
      const res = await api.get("/admin/products", { params: { page: p, limit: 10 } });
      setProducts(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotal(res.data.total);
    } catch {
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchProducts(page); }, [page]);

  const toggleActive = async (productId, isActive) => {
    await api.patch(`/admin/products/${productId}`, { is_active: !isActive });
    fetchProducts(page);
  };

  const handleDelete = async (productId) => {
    if (!window.confirm("Delete this product?")) return;
    await api.delete(`/admin/products/${productId}`);
    fetchProducts(page);
  };

  return (
    <div className="page">
      <div className="container">
        <h1>Manage Products</h1>
        <p className="subtitle">{total} product{total !== 1 ? "s" : ""}</p>

        {loading ? <Loading /> : (
          <div className="admin-table">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Seller</th>
                  <th>Price</th>
                  <th>Stock</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.id}>
                    <td>{p.name}</td>
                    <td>{p.seller_name || "—"}</td>
                    <td>৳{p.price.toFixed(2)}</td>
                    <td>{p.stock}</td>
                    <td>
                      <span className={`badge ${p.is_active ? "badge-active" : "badge-inactive"}`}>
                        {p.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="actions-cell">
                      <button className="btn btn-outline btn-sm" onClick={() => toggleActive(p.id, p.is_active)}>
                        {p.is_active ? "Deactivate" : "Activate"}
                      </button>
                      <button className="btn btn-outline btn-sm btn-danger-text" onClick={() => handleDelete(p.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {totalPages > 1 && (
          <div className="pagination">
            <button className="btn btn-outline btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
            <span className="pagination-info">Page {page} of {totalPages}</span>
            <button className="btn btn-outline btn-sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</button>
          </div>
        )}
      </div>
    </div>
  );
}
