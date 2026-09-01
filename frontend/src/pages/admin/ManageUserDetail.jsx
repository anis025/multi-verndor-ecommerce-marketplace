import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { adminUsersService } from "../../services/adminUsersService";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";
import ConfirmDialog from "../../components/dashboard/ConfirmDialog";
import { useToast } from "../../context/ToastContext";

const formatDate = (v) => {
  if (!v) return "—";
  const d = new Date(v);
  return isNaN(d) ? "—" : d.toLocaleString();
};

const STATUS_COLORS = {
  pending: "#f59e0b",
  confirmed: "#2563eb",
  processing: "#7c3aed",
  shipped: "#0ea5e9",
  delivered: "#16a34a",
  cancelled: "#dc2626",
};

export default function ManageUserDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [confirmReset, setConfirmReset] = useState(false);
  const [resetPwd, setResetPwd] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminUsersService.getById(id);
      setUser(data);
    } catch (err) {
      setError(err.response?.data?.detail || "User not found.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const toggleStatus = async () => {
    try {
      await adminUsersService.updateStatus(user.id, !user.is_active);
      toast.success(`User ${!user.is_active ? "activated" : "blocked"}.`);
      load();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update status.");
    }
  };

  const doReset = async () => {
    setConfirmReset(false);
    try {
      const data = await adminUsersService.resetPassword(user.id);
      setResetPwd(data.new_password);
      toast.success("Password reset.");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to reset password.");
    }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="container"><Loading /></div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="page">
        <div className="container">
          <button className="btn btn-outline" onClick={() => navigate("/admin/users")}>← Back</button>
          <ErrorMessage message={error} />
        </div>
      </div>
    );
  }
  if (!user) return null;

  return (
    <div className="page">
      <div className="container">
        <button className="btn btn-outline" onClick={() => navigate("/admin/users")}>← Back to Users</button>
        <h1 style={{ marginTop: 16 }}>{user.name}</h1>
        <p className="subtitle">{user.email}</p>

        <section className="card" style={{ marginTop: 16 }}>
          <h2>Profile</h2>
          <div className="order-detail-row"><span>Role</span><span><span className={`badge badge-${user.role}`}>{user.role}</span></span></div>
          <div className="order-detail-row"><span>Status</span><span>{user.is_active ? "Active" : "Blocked"}</span></div>
          <div className="order-detail-row"><span>Email Verified</span><span>{user.email_verified ? "Yes" : "No"}</span></div>
          <div className="order-detail-row"><span>Joined</span><span>{formatDate(user.created_at)}</span></div>
          <div className="order-detail-row"><span>Last updated</span><span>{formatDate(user.updated_at)}</span></div>
          {user.seller_id && (
            <>
              <div className="order-detail-row"><span>Seller ID</span><span>{user.seller_id}</span></div>
              <div className="order-detail-row"><span>Company</span><span>{user.company_name}</span></div>
              <div className="order-detail-row"><span>Seller status</span><span>{user.seller_status}</span></div>
              <div className="order-detail-row"><span>Products</span><span>{user.product_count ?? 0}</span></div>
            </>
          )}
          {user.role === "customer" && (
            <div className="order-detail-row"><span>Orders</span><span>{user.order_count ?? 0}</span></div>
          )}
        </section>

        <section className="card" style={{ marginTop: 16 }}>
          <h2>Actions</h2>
          <div className="admin-table-actions">
            <button
              className={`btn ${user.is_active ? "btn-danger" : "btn-outline"}`}
              onClick={toggleStatus}
            >
              {user.is_active ? "Block user" : "Activate user"}
            </button>
            <button className="btn btn-outline" onClick={() => setConfirmReset(true)}>
              Reset password
            </button>
            <Link to="/admin/users" className="btn btn-outline">Back</Link>
          </div>
        </section>

        {user.role === "customer" && user.recent_orders?.length > 0 && (
          <section className="card" style={{ marginTop: 16 }}>
            <h2>Recent Orders</h2>
            <table>
              <thead>
                <tr>
                  <th>Order</th>
                  <th>Date</th>
                  <th>Items</th>
                  <th>Status</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {user.recent_orders.map((o) => (
                  <tr key={o.id}>
                    <td>#{o.id.slice(-8).toUpperCase()}</td>
                    <td>{formatDate(o.created_at)}</td>
                    <td>{o.item_count}</td>
                    <td>
                      <span style={{ color: STATUS_COLORS[o.status] || "#6b7280", fontWeight: 600, textTransform: "capitalize" }}>
                        {o.status}
                      </span>
                    </td>
                    <td>৳{o.total_amount.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </div>

      <ConfirmDialog
        open={confirmReset}
        title="Reset this user's password?"
        message="A new strong password will be generated and shown to you ONCE."
        confirmLabel="Reset password"
        onConfirm={doReset}
        onCancel={() => setConfirmReset(false)}
      />

      {resetPwd && (
        <div className="modal-backdrop" onClick={() => setResetPwd(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>New password</h3>
              <button className="modal-close" onClick={() => setResetPwd(null)}>×</button>
            </div>
            <div className="modal-body">
              <p>Share this with <strong>{user.email}</strong> securely. It won't be shown again.</p>
              <div className="dash-coupon-code-row" style={{ marginTop: 12 }}>
                <code className="dash-coupon-code">{resetPwd}</code>
                <button className="btn btn-outline btn-sm" onClick={() => navigator.clipboard?.writeText(resetPwd)}>Copy</button>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-primary" onClick={() => setResetPwd(null)}>Done</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
