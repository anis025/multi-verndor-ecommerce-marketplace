import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../../services/api";
import Loading from "../../components/Loading";

export default function SellerProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const fetchProducts = async (p) => {
    setLoading(true);
    try {
      const res = await api.get("/sellers/me/products", { params: { page: p, limit: 10 } });
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

  const handleDelete = async (productId) => {
    if (!window.confirm("Are you sure you want to delete this product?")) return;
    try {
      await api.delete(`/sellers/me/products/${productId}`);
      fetchProducts(page);
    } catch {
      // silent
    }
  };

  if (loading && products.length === 0) return <Loading />;

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <h1>My Products</h1>
          <Link to="/seller/products/new" className="btn btn-primary">Add Product</Link>
        </div>
        <p className="subtitle">{total} product{total !== 1 ? "s" : ""}</p>

        {products.length === 0 ? (
          <div className="empty-state">
            <p>No products yet.</p>
            <Link to="/seller/products/new" className="btn btn-primary" style={{ marginTop: 16 }}>
              Add Your First Product
            </Link>
          </div>
        ) : (
          <div className="seller-products-table">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Price</th>
                  <th>Stock</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.id}>
                    <td className="product-cell">
                      <img src={p.image_url || "/placeholder.png"} alt={p.name} className="product-thumb" />
                      <span>{p.name}</span>
                    </td>
                    <td>৳{p.price.toFixed(2)}</td>
                    <td>{p.stock}</td>
                    <td>
                      <span className={`badge ${p.is_active ? "badge-active" : "badge-inactive"}`}>
                        {p.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="actions-cell">
                      <Link to={`/seller/products/${p.id}/edit`} className="btn btn-outline btn-sm">Edit</Link>
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
