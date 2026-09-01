import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../../services/api";
import Loading from "../../components/Loading";

const STATUS_OPTIONS = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"];
const STATUS_COLORS = {
  pending: "#f59e0b",
  confirmed: "#2563eb",
  processing: "#7c3aed",
  shipped: "#0ea5e9",
  delivered: "#16a34a",
  cancelled: "#dc2626",
};

export default function ManageOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const fetchOrders = async (p) => {
    setLoading(true);
    try {
      const res = await api.get("/admin/orders", { params: { page: p, limit: 10 } });
      setOrders(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotal(res.data.total);
    } catch {
      setOrders([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchOrders(page); }, [page]);

  const handleStatusUpdate = async (orderId, status) => {
    await api.put(`/admin/orders/${orderId}/status`, { status });
    fetchOrders(page);
  };

  return (
    <div className="page">
      <div className="container">
        <h1>Manage Orders</h1>
        <p className="subtitle">{total} order{total !== 1 ? "s" : ""}</p>

        {loading ? <Loading /> : (
          <div className="admin-table">
            <table>
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Items</th>
                  <th>Total</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((o) => (
                  <tr key={o.id}>
                    <td className="order-id">#{o.id.slice(-8).toUpperCase()}</td>
                    <td>{o.items.map((i) => i.product_name).join(", ")}</td>
                    <td>৳{o.total_amount.toFixed(2)}</td>
                    <td>
                      <select
                        className="status-select"
                        value={o.status}
                        onChange={(e) => handleStatusUpdate(o.id, e.target.value)}
                        style={{ color: STATUS_COLORS[o.status] || "#6b7280" }}
                      >
                        {STATUS_OPTIONS.map((s) => (
                          <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                        ))}
                      </select>
                    </td>
                    <td>{new Date(o.created_at).toLocaleDateString()}</td>
                    <td>
                      <Link to={`/admin/orders/${o.id}`} className="btn btn-outline btn-sm">Details</Link>
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
