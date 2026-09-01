import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../../services/api";
import Loading from "../../components/Loading";

export default function SellerDashboard() {
  const [stats, setStats] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [profileRes, productsRes, ordersRes, notifRes] = await Promise.all([
          api.get("/sellers/me"),
          api.get("/sellers/me/products", { params: { limit: 100 } }),
          api.get("/seller/orders", { params: { limit: 100 } }),
          api.get("/notifications", { params: { limit: 5 } }),
        ]);
        setStats({
          company: profileRes.data.company_name,
          is_approved: profileRes.data.is_approved,
          total_products: productsRes.data.total,
          total_orders: ordersRes.data.total,
          unread_notifications: notifRes.data.unread_count,
        });
        setNotifications(notifRes.data.items);
      } catch {
        // silent
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <Loading />;

  return (
    <div className="page">
      <div className="container">
        <h1>Seller Dashboard</h1>
        {stats && (
          <>
            <p className="subtitle">{stats.company}</p>
            {!stats.is_approved && (
              <div className="alert alert-warning" style={{ marginBottom: 16 }}>
                Your seller account is pending approval. You cannot add products until approved.
              </div>
            )}
            <div className="dashboard-stats">
              <div className="stat-card">
                <span className="stat-value">{stats.total_products}</span>
                <span className="stat-label">Products</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{stats.total_orders}</span>
                <span className="stat-label">Orders</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{stats.unread_notifications}</span>
                <span className="stat-label">Unread Notifications</span>
              </div>
            </div>

            <div className="dashboard-actions">
              <Link to="/seller/products" className="btn btn-primary">My Products</Link>
              <Link to="/seller/orders" className="btn btn-outline">My Orders</Link>
              <Link to="/seller/notifications" className="btn btn-outline">Notifications</Link>
            </div>

            {notifications.length > 0 && (
              <div className="dashboard-section">
                <h3>Recent Notifications</h3>
                {notifications.map((n) => (
                  <div key={n.id} className={`notification-item ${n.is_read ? "" : "unread"}`}>
                    <strong>{n.title}</strong>
                    <p>{n.message}</p>
                    <span className="notification-date">{new Date(n.created_at).toLocaleDateString()}</span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
