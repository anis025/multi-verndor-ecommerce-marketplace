import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { orderService } from "../../services/orderService";
import { Skeleton, SkeletonRow } from "../../components/dashboard/Skeleton";
import ProgressTimeline from "../../components/dashboard/ProgressTimeline";
import ConfirmDialog from "../../components/dashboard/ConfirmDialog";
import { useToast } from "../../context/ToastContext";
import { IconChevronRight, IconMapPin, IconCard, IconClock } from "../../components/dashboard/Icon";

const formatDate = (v) => {
  if (!v) return "";
  const d = new Date(v);
  return isNaN(d) ? "" : d.toLocaleString();
};

export default function OrderDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState(null);
  const [confirmCancel, setConfirmCancel] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    setOrder(null);
    setError(null);
    orderService
      .getById(id)
      .then(setOrder)
      .catch((err) => setError(err.response?.data?.detail || "Order not found."));
  }, [id]);

  const handleCancel = async () => {
    setCancelling(true);
    try {
      await orderService.cancel(id);
      toast.success("Order cancelled.");
      const updated = await orderService.getById(id);
      setOrder(updated);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to cancel order.");
    } finally {
      setCancelling(false);
      setConfirmCancel(false);
    }
  };

  if (error) {
    return (
      <div className="dash-page">
        <div className="alert alert-error">{error}</div>
        <button className="btn btn-outline" onClick={() => navigate("/dashboard/orders")}>
          ← Back to Orders
        </button>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="dash-page">
        <div className="dash-card">
          <Skeleton height={20} width="40%" style={{ marginBottom: 16 }} />
          <SkeletonRow cols={4} />
          <SkeletonRow cols={2} style={{ marginTop: 12 }} />
        </div>
      </div>
    );
  }

  const subtotal = order.items.reduce((s, i) => s + i.subtotal, 0);
  const shipping = 0; // Demo only — adjust when real shipping fields are added.
  const discount = 0;
  const total = order.total_amount;

  return (
    <div className="dash-page">
      <header className="dash-page-header">
        <div>
          <button
            className="btn-link dash-back"
            onClick={() => navigate("/dashboard/orders")}
          >
            ← Back to Orders
          </button>
          <h1>Order #{order.id.slice(-8).toUpperCase()}</h1>
          <p className="dash-muted">Placed on {formatDate(order.created_at)}</p>
        </div>
        {order.status === "pending" && (
          <button
            className="btn btn-outline"
            onClick={() => setConfirmCancel(true)}
            disabled={cancelling}
          >
            {cancelling ? "Cancelling…" : "Cancel Order"}
          </button>
        )}
      </header>

      <section className="dash-card">
        <h2 className="dash-section-title">Status</h2>
        <ProgressTimeline status={order.status} />
      </section>

      <section className="dash-card">
        <h2 className="dash-section-title">Items</h2>
        <ul className="dash-items">
          {order.items.map((it, i) => (
            <li key={i} className="dash-item-row">
              <div className="dash-item-info">
                <div className="dash-item-name">{it.product_name}</div>
                <div className="dash-muted">Sold by {it.seller_name || "—"}</div>
              </div>
              <div className="dash-item-qty">x{it.quantity}</div>
              <div className="dash-item-price">৳{it.unit_price.toFixed(2)}</div>
              <div className="dash-item-subtotal">৳{it.subtotal.toFixed(2)}</div>
            </li>
          ))}
        </ul>
      </section>

      <div className="dash-grid-2">
        <section className="dash-card">
          <h2 className="dash-section-title">
            <IconMapPin size={18} /> Shipping Address
          </h2>
          <p className="dash-strong">{order.shipping_address?.name}</p>
          <p>{order.shipping_address?.phone}</p>
          <p>{order.shipping_address?.address}</p>
        </section>

        <section className="dash-card">
          <h2 className="dash-section-title">
            <IconCard size={18} /> Payment
          </h2>
          <p className="dash-muted">Method on file</p>
          <p className="dash-strong">Visa •••• 4242</p>
        </section>
      </div>

      <section className="dash-card">
        <h2 className="dash-section-title">Price Breakdown</h2>
        <div className="dash-price-row"><span>Subtotal</span><span>৳{subtotal.toFixed(2)}</span></div>
        <div className="dash-price-row"><span>Shipping</span><span>{shipping ? `৳${shipping.toFixed(2)}` : "Free"}</span></div>
        <div className="dash-price-row"><span>Discount</span><span>{discount ? `-৳${discount.toFixed(2)}` : "—"}</span></div>
        <div className="dash-price-row dash-price-total"><span>Total</span><span>৳{total.toFixed(2)}</span></div>
      </section>

      <ConfirmDialog
        open={confirmCancel}
        title="Cancel this order?"
        message="This will cancel your order. This action cannot be undone."
        confirmLabel="Yes, cancel"
        onConfirm={handleCancel}
        onCancel={() => setConfirmCancel(false)}
      />
    </div>
  );
}
