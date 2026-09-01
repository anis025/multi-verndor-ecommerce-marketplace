import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import Loading from "../components/Loading";

const STATUS_COLORS = {
  pending: "#f59e0b",
  confirmed: "#2563eb",
  processing: "#7c3aed",
  shipped: "#0ea5e9",
  delivered: "#16a34a",
  cancelled: "#dc2626",
};

const STATUS_OPTIONS = ["", "pending", "confirmed", "processing", "shipped", "delivered", "cancelled"];

const formatDateTime = (value) => {
  if (!value) return "";
  const d = new Date(value);
  return isNaN(d) ? value : d.toLocaleString();
};

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true);
      try {
        const params = { page, limit: 10 };
        if (statusFilter) params.status = statusFilter;
        const res = await api.get("/orders", { params });
        setOrders(res.data.items);
        setTotalPages(res.data.total_pages);
        setTotal(res.data.total);
      } catch {
        setOrders([]);
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, [page, statusFilter]);

  if (loading) return <Loading />;

  if (orders.length === 0) {
    return (
      <div className="page">
        <div className="container">
          <h1>My Orders</h1>
          <div className="empty-state">
            <p>You haven't placed any orders yet.</p>
            <Link to="/" className="btn btn-primary" style={{ marginTop: 16 }}>
              Browse Products
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <h1>My Orders</h1>
        <p className="subtitle">{total} order{total !== 1 ? "s" : ""}</p>

        <div className="filter-bar">
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
            <option value="">All Statuses</option>
            {STATUS_OPTIONS.filter((s) => s).map((s) => (
              <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>
        </div>

        <div className="orders-list">
          {orders.map((order) => (
            <Link to={`/orders/${order.id}`} key={order.id} className="order-card">
              <div className="order-card-header">
                <span className="order-id">#{order.id.slice(-8).toUpperCase()}</span>
                <span
                  className="order-status"
                  style={{ color: STATUS_COLORS[order.status] || "#6b7280" }}
                >
                  {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                </span>
              </div>
              <div className="order-card-items">
                {order.items.slice(0, 3).map((item, i) => (
                  <span key={i}>
                    {item.product_name} x{item.quantity}
                    {i < Math.min(order.items.length, 3) - 1 ? ", " : ""}
                  </span>
                ))}
                {order.items.length > 3 && <span> +{order.items.length - 3} more</span>}
              </div>
              <div className="order-card-footer">
                <span className="order-date">{formatDateTime(order.created_at)}</span>
                <span className="order-total">৳{order.total_amount.toFixed(2)}</span>
              </div>
            </Link>
          ))}
        </div>

        {totalPages > 1 && (
          <div className="pagination">
            <button className="btn btn-outline btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
              Previous
            </button>
            <span className="pagination-info">Page {page} of {totalPages}</span>
            <button className="btn btn-outline btn-sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
