import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../services/api";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";

const STATUS_OPTIONS = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"];
const STATUS_COLORS = {
  pending: "#f59e0b",
  confirmed: "#2563eb",
  processing: "#7c3aed",
  shipped: "#0ea5e9",
  delivered: "#16a34a",
  cancelled: "#dc2626",
};

export default function AdminOrderDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOrder = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/admin/orders/${id}`);
      setOrder(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Order not found.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchOrder(); }, [id]);

  const handleStatusUpdate = async (status) => {
    await api.put(`/admin/orders/${id}/status`, { status });
    fetchOrder();
  };

  if (loading) return <Loading />;
  if (error) return <div className="page"><div className="container"><ErrorMessage message={error} /></div></div>;
  if (!order) return null;

  return (
    <div className="page">
      <div className="container">
        <button className="btn btn-outline btn-back" onClick={() => navigate("/admin/orders")}>
          &larr; Back to Orders
        </button>
        <h1>Order #{order.id.slice(-8).toUpperCase()}</h1>

        <div className="order-detail-layout">
          <div className="order-detail-main">
            <div className="order-detail-section">
              <h3>Items</h3>
              {order.items.map((item, i) => (
                <div key={i} className="order-detail-item">
                  <div className="order-detail-item-info">
                    <span className="order-detail-item-name">{item.product_name}</span>
                    <span className="order-detail-item-seller">by {item.seller_name}</span>
                  </div>
                  <div className="order-detail-item-qty">
                    {item.quantity} x ৳{item.unit_price.toFixed(2)}
                  </div>
                  <div className="order-detail-item-subtotal">
                    ৳{item.subtotal.toFixed(2)}
                  </div>
                  <span
                    className="order-detail-item-status"
                    style={{ color: STATUS_COLORS[item.seller_status] || "#6b7280" }}
                  >
                    {item.seller_status.charAt(0).toUpperCase() + item.seller_status.slice(1)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="order-detail-sidebar">
            <div className="order-detail-section">
              <h3>Summary</h3>
              <div className="order-detail-row">
                <span>Status</span>
                <select
                  className="status-select"
                  value={order.status}
                  onChange={(e) => handleStatusUpdate(e.target.value)}
                  style={{ color: STATUS_COLORS[order.status] || "#6b7280" }}
                >
                  {STATUS_OPTIONS.map((s) => (
                    <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                  ))}
                </select>
              </div>
              <div className="order-detail-row">
                <span>Total</span>
                <span className="order-detail-total">৳{order.total_amount.toFixed(2)}</span>
              </div>
              <div className="order-detail-row">
                <span>Date</span>
                <span>{new Date(order.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            <div className="order-detail-section">
              <h3>Shipping</h3>
              <p>{order.shipping_address.name}</p>
              <p>{order.shipping_address.phone}</p>
              <p>{order.shipping_address.address}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
