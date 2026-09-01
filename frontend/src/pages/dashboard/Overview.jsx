import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { orderService } from "../../services/orderService";
import { wishlistService } from "../../services/wishlistService";
import { MOCK_RECOMMENDED, MOCK_RECENTLY_VIEWED } from "../../data/mockData";
import StatCard from "../../components/dashboard/StatCard";
import { Skeleton, SkeletonCard } from "../../components/dashboard/Skeleton";
import {
  IconBox,
  IconCart,
  IconChevronRight,
  IconHeart,
  IconPackage,
  IconPlus,
  IconStar,
  IconTruck,
  IconUser,
} from "../../components/dashboard/Icon";

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

export default function Overview() {
  const { user } = useAuth();
  const [orders, setOrders] = useState(null);
  const [wishlist, setWishlist] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    setError(null);
    orderService
      .list({ page: 1, limit: 50 })
      .then((res) => setOrders(res.items || []))
      .catch(() => setError("Could not load orders."));

    wishlistService.list().then(setWishlist).catch(() => {});
  }, []);

  const total = orders?.length ?? 0;
  const active =
    orders?.filter((o) => ["pending", "confirmed", "processing", "shipped"].includes(o.status))
      .length ?? 0;
  const delivered = orders?.filter((o) => o.status === "delivered").length ?? 0;
  const wishlistCount = wishlist.length;

  const firstName = (user?.name || "").split(" ")[0] || "there";

  return (
    <div className="dash-page">
      <header className="dash-page-header">
        <div>
          <h1>Hi, {firstName} 👋</h1>
          <p className="dash-muted">Here's a quick look at your account activity.</p>
        </div>
        <div className="dash-quick-actions">
          <Link to="/" className="btn btn-outline">
            <IconPlus size={16} /> Browse
          </Link>
          <Link to="/dashboard/cart" className="btn btn-primary">
            <IconCart size={16} /> View Cart
          </Link>
        </div>
      </header>

      <section className="dash-stats">
        {orders === null ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <StatCard icon={IconBox} label="Total Orders" value={total} />
            <StatCard icon={IconTruck} label="Active Orders" value={active} tone="info" />
            <StatCard icon={IconPackage} label="Delivered" value={delivered} tone="success" />
            <StatCard icon={IconHeart} label="Wishlist Items" value={wishlistCount} tone="warn" />
          </>
        )}
      </section>

      {error && <div className="alert alert-error">{error}</div>}

      <section className="dash-card">
        <div className="dash-card-head">
          <h2>Recent Orders</h2>
          <Link to="/dashboard/orders" className="dash-link">
            View all <IconChevronRight size={14} />
          </Link>
        </div>
        {orders === null ? (
          <div className="dash-list">
            <Skeleton height={48} style={{ marginBottom: 8 }} />
            <Skeleton height={48} style={{ marginBottom: 8 }} />
            <Skeleton height={48} />
          </div>
        ) : orders.length === 0 ? (
          <p className="dash-muted">You haven't placed any orders yet.</p>
        ) : (
          <ul className="dash-mini-list">
            {orders.slice(0, 4).map((o) => (
              <li key={o.id} className="dash-mini-item">
                <div>
                  <div className="dash-mini-title">#{o.id.slice(-8).toUpperCase()}</div>
                  <div className="dash-muted">
                    {o.items.length} item{o.items.length !== 1 ? "s" : ""} · {formatDate(o.created_at)}
                  </div>
                </div>
                <div
                  className="dash-mini-status"
                  style={{ color: STATUS_COLORS[o.status] }}
                >
                  {o.status}
                </div>
                <div className="dash-mini-amount">৳{o.total_amount.toFixed(2)}</div>
                <Link to={`/dashboard/orders/${o.id}`} className="dash-link">
                  <IconChevronRight size={16} />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <div className="dash-grid-2">
        <section className="dash-card">
          <div className="dash-card-head">
            <h2>Recently Viewed</h2>
          </div>
          <div className="dash-thumb-grid">
            {MOCK_RECENTLY_VIEWED.map((p) => (
              <article key={p.id} className="dash-thumb-card">
                <img src={p.image_url} alt={p.name} loading="lazy" />
                <div className="dash-thumb-body">
                  <div className="dash-thumb-title">{p.name}</div>
                  <div className="dash-thumb-price">৳{p.price.toFixed(2)}</div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="dash-card">
          <div className="dash-card-head">
            <h2>Recommended for You</h2>
          </div>
          <div className="dash-thumb-grid">
            {MOCK_RECOMMENDED.map((p) => (
              <article key={p.id} className="dash-thumb-card">
                <img src={p.image_url} alt={p.name} loading="lazy" />
                <div className="dash-thumb-body">
                  <div className="dash-thumb-title">{p.name}</div>
                  <div className="dash-thumb-price">৳{p.price.toFixed(2)}</div>
                  <button className="btn btn-outline btn-sm">
                    <IconStar size={14} /> Add
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
