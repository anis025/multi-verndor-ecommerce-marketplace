import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../../services/api";
import Loading from "../../components/Loading";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/admin/dashboard")
      .then((res) => setStats(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;

  return (
    <div className="page">
      <div className="container">
        <h1>Admin Dashboard</h1>
        <p className="subtitle">Platform Overview</p>

        {stats && (
          <div className="dashboard-stats">
            <div className="stat-card">
              <span className="stat-value">{stats.total_users}</span>
              <span className="stat-label">Customers</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{stats.total_sellers}</span>
              <span className="stat-label">Sellers</span>
            </div>
            <div className="stat-card">
              <span className="stat-value" style={{ color: stats.pending_sellers > 0 ? "#f59e0b" : undefined }}>
                {stats.pending_sellers}
              </span>
              <span className="stat-label">Pending Sellers</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{stats.total_products}</span>
              <span className="stat-label">Products</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{stats.total_orders}</span>
              <span className="stat-label">Orders</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">৳{stats.total_revenue.toFixed(2)}</span>
              <span className="stat-label">Revenue</span>
            </div>
          </div>
        )}

        <div className="dashboard-actions">
          <Link to="/admin/users" className="btn btn-primary">Manage Users</Link>
          <Link to="/admin/sellers" className="btn btn-outline">Manage Sellers</Link>
          <Link to="/admin/products" className="btn btn-outline">Manage Products</Link>
          <Link to="/admin/categories" className="btn btn-outline">Manage Categories</Link>
          <Link to="/admin/orders" className="btn btn-outline">Manage Orders</Link>
          <Link to="/admin/settings" className="btn btn-outline">System Settings</Link>
          <Link to="/admin/audit" className="btn btn-outline">Audit Log</Link>
        </div>
      </div>
    </div>
  );
}
