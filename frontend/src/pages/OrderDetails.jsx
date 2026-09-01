import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

const STATUS_COLORS = {
  pending: "#f59e0b",
  confirmed: "#2563eb",
  processing: "#7c3aed",
  shipped: "#0ea5e9",
  delivered: "#16a34a",
  cancelled: "#dc2626",
};

const formatDateTime = (value) => {
  if (!value) return "";
  const d = new Date(value);
  return isNaN(d) ? value : d.toLocaleString();
};

export default function OrderDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cancelling, setCancelling] = useState(false);
  const [cancelError, setCancelError] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get(`/orders/${id}`);
      setOrder(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Order not found.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const handleCancel = async () => {
    if (!window.confirm("Cancel this order? This cannot be undone.")) return;
    setCancelling(true);
    setCancelError(null);
    try {
      await api.patch(`/orders/${id}/cancel`);
      await load();
    } catch (err) {
      setCancelError(err.response?.data?.detail || "Failed to cancel order.");
    } finally {
      setCancelling(false);
    }
  };

  if (loading) return <Loading />;
  if (error) return <div className="page"><div className="container"><ErrorMessage message={error} /></div></div>;
  if (!order) return null;

  return (
    <div className="page">
      <div className="container">
        <button className="btn btn-outline btn-back" onClick={() => navigate("/orders")}>
          &larr; Back to Orders
        </button>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
          <h1>Order #{order.id.slice(-8).toUpperCase()}</h1>
          {order.status === "pending" && (
            <button className="btn btn-outline btn-danger-text" onClick={handleCancel} disabled={cancelling}>
              {cancelling ? "Cancelling..." : "Cancel Order"}
            </button>
          )}
        </div>
        {cancelError && <div className="alert alert-error">{cancelError}</div>}

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
                <span style={{ color: STATUS_COLORS[order.status] || "#6b7280", fontWeight: 600 }}>
                  {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                </span>
              </div>
              <div className="order-detail-row">
                <span>Total</span>
                <span className="order-detail-total">৳{order.total_amount.toFixed(2)}</span>
              </div>
              <div className="order-detail-row">
                <span>Placed</span>
                <span>{formatDateTime(order.created_at)}</span>
              </div>
              <div className="order-detail-row">
                <span>Last updated</span>
                <span>{formatDateTime(order.updated_at)}</span>
              </div>
            </div>

            <div className="order-detail-section">
              <h3>Shipping Address</h3>
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
