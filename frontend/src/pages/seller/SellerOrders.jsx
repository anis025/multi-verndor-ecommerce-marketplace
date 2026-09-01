import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../../services/api";
import Loading from "../../components/Loading";

const STATUS_COLORS = {
  pending: "#f59e0b",
  confirmed: "#2563eb",
  processing: "#7c3aed",
  shipped: "#0ea5e9",
  delivered: "#16a34a",
  cancelled: "#dc2626",
};

export default function SellerOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true);
      try {
        const res = await api.get("/seller/orders", { params: { page, limit: 10 } });
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
  }, [page]);

  if (loading) return <Loading />;

  if (orders.length === 0) {
    return (
      <div className="page">
        <div className="container">
          <h1>My Orders</h1>
          <div className="empty-state"><p>No orders yet.</p></div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <h1>My Orders</h1>
        <p className="subtitle">{total} order{total !== 1 ? "s" : ""}</p>

        <div className="orders-list">
          {orders.map((order) => (
            <Link to={`/seller/orders/${order.id}`} key={order.id} className="order-card">
              <div className="order-card-header">
                <span className="order-id">#{order.id.slice(-8).toUpperCase()}</span>
                <span className="order-status" style={{ color: STATUS_COLORS[order.status] || "#6b7280" }}>
                  {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                </span>
              </div>
              <div className="order-card-items">
                {order.items.map((item, i) => (
                  <span key={i}>
                    {item.product_name} x{item.quantity}
                    {i < order.items.length - 1 ? ", " : ""}
                  </span>
                ))}
              </div>
              <div className="order-card-footer">
                <span className="order-date">{new Date(order.created_at).toLocaleDateString()}</span>
                <span className="order-total">৳{order.total_amount.toFixed(2)}</span>
              </div>
            </Link>
          ))}
        </div>

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
