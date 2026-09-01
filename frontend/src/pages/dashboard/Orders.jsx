import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { orderService } from "../../services/orderService";
import { Skeleton, SkeletonRow } from "../../components/dashboard/Skeleton";
import EmptyState from "../../components/dashboard/EmptyState";
import { IconBox, IconChevronRight, IconSearch } from "../../components/dashboard/Icon";

const STATUS_OPTIONS = ["", "pending", "confirmed", "processing", "shipped", "delivered", "cancelled"];
const STATUS_COLORS = {
  pending: "#f59e0b",
  confirmed: "#2563eb",
  processing: "#7c3aed",
  shipped: "#0ea5e9",
  delivered: "#16a34a",
  cancelled: "#dc2626",
};

const formatDate = (v) => {
  if (!v) return "";
  const d = new Date(v);
  return isNaN(d) ? "" : d.toLocaleDateString();
};

export default function Orders() {
  const [orders, setOrders] = useState(null);
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    setError(null);
    setOrders(null);
    orderService
      .list({ page: 1, limit: 50, ...(status ? { status } : {}) })
      .then((res) => setOrders(res.items || []))
      .catch(() => {
        setError("Failed to load orders.");
        setOrders([]);
      });
  }, [status]);

  const filtered = (orders || []).filter((o) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      o.id.toLowerCase().includes(q) ||
      o.items.some((i) => i.product_name.toLowerCase().includes(q))
    );
  });

  return (
    <div className="dash-page">
      <header className="dash-page-header">
        <div>
          <h1>My Orders</h1>
          <p className="dash-muted">Track, search, and review all your orders.</p>
        </div>
      </header>

      <div className="dash-toolbar">
        <div className="dash-search">
          <IconSearch size={16} />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by order ID or product…"
            aria-label="Search orders"
          />
        </div>
        <select
          className="dash-select"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          aria-label="Filter by status"
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s ? s[0].toUpperCase() + s.slice(1) : "All Statuses"}
            </option>
          ))}
        </select>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {orders === null ? (
        <div className="dash-card">
          <SkeletonRow cols={4} />
          <SkeletonRow cols={4} style={{ marginTop: 8 }} />
          <SkeletonRow cols={4} style={{ marginTop: 8 }} />
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={IconBox}
          title="No orders found"
          description={
            search || status
              ? "Try adjusting your filters."
              : "When you place an order, it will appear here."
          }
          actionLabel="Browse Products"
          actionTo="/"
        />
      ) : (
        <>
          <div className="dash-card dash-table-wrap">
            <table className="dash-table">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Date</th>
                  <th>Items</th>
                  <th>Status</th>
                  <th>Total</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((o) => (
                  <tr key={o.id}>
                    <td className="dash-mono">#{o.id.slice(-8).toUpperCase()}</td>
                    <td>{formatDate(o.created_at)}</td>
                    <td>
                      <div className="dash-item-names">
                        {o.items.slice(0, 2).map((i, idx) => (
                          <span key={idx}>
                            {i.product_name}
                            {idx < Math.min(o.items.length, 2) - 1 ? ", " : ""}
                          </span>
                        ))}
                        {o.items.length > 2 && ` +${o.items.length - 2} more`}
                      </div>
                    </td>
                    <td>
                      <span
                        className="dash-status-pill"
                        style={{
                          color: STATUS_COLORS[o.status],
                          borderColor: STATUS_COLORS[o.status],
                        }}
                      >
                        {o.status}
                      </span>
                    </td>
                    <td className="dash-strong">৳{o.total_amount.toFixed(2)}</td>
                    <td>
                      <Link to={`/dashboard/orders/${o.id}`} className="dash-link">
                        Details <IconChevronRight size={14} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="dash-cards-list">
            {filtered.map((o) => (
              <Link key={o.id} to={`/dashboard/orders/${o.id}`} className="dash-order-card-mobile">
                <div className="dash-order-card-top">
                  <span className="dash-mono">#{o.id.slice(-8).toUpperCase()}</span>
                  <span
                    className="dash-status-pill"
                    style={{ color: STATUS_COLORS[o.status], borderColor: STATUS_COLORS[o.status] }}
                  >
                    {o.status}
                  </span>
                </div>
                <div className="dash-muted">{formatDate(o.created_at)} · {o.items.length} item(s)</div>
                <div className="dash-order-card-bottom">
                  <span className="dash-strong">৳{o.total_amount.toFixed(2)}</span>
                  <span className="dash-link">View <IconChevronRight size={14} /></span>
                </div>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
