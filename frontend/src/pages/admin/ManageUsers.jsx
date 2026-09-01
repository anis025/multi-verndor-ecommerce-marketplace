import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { adminUsersService } from "../../services/adminUsersService";
import { useToast } from "../../context/ToastContext";
import Loading from "../../components/Loading";
import ConfirmDialog from "../../components/dashboard/ConfirmDialog";

export default function ManageUsers() {
  const toast = useToast();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  // Action state
  const [confirmReset, setConfirmReset] = useState(null); // user object
  const [resetResult, setResetResult] = useState(null); // {new_password, email}
  const [roleTarget, setRoleTarget] = useState(null);
  const [roleValue, setRoleValue] = useState("customer");
  const [confirmVerify, setConfirmVerify] = useState(null);

  const fetchUsers = async (p) => {
    setLoading(true);
    try {
      const params = { page: p, limit: 10 };
      if (roleFilter) params.role = roleFilter;
      if (statusFilter === "active") params.role = params.role || undefined;
      const res = await adminUsersService.list(params);
      setUsers(res.items);
      setTotalPages(res.total_pages || Math.ceil((res.total || 0) / 10));
      setTotal(res.total || 0);
    } catch {
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(page); }, [page, roleFilter]); // status filter not sent (server returns all)
  // Re-fetch when statusFilter changes
  useEffect(() => { setPage(1); fetchUsers(1); }, [statusFilter]);

  const toggleStatus = async (u) => {
    try {
      await adminUsersService.updateStatus(u.id, !u.is_active);
      toast.success(`User ${!u.is_active ? "activated" : "deactivated"}.`);
      fetchUsers(page);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update status.");
    }
  };

  const doReset = async () => {
    const u = confirmReset;
    setConfirmReset(null);
    try {
      const data = await adminUsersService.resetPassword(u.id);
      setResetResult({ email: u.email, new_password: data.new_password });
      toast.success("Password reset. Share it with the user securely.");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to reset password.");
    }
  };

  const doChangeRole = async () => {
    if (!roleTarget) return;
    try {
      await adminUsersService.changeRole(roleTarget.id, roleValue);
      toast.success(`Role updated to "${roleValue}".`);
      setRoleTarget(null);
      fetchUsers(page);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to change role.");
    }
  };

  const doVerifyEmail = async () => {
    if (!confirmVerify) return;
    try {
      await adminUsersService.verifyEmail(confirmVerify.id);
      toast.success("Email marked as verified.");
      setConfirmVerify(null);
      fetchUsers(page);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to verify email.");
    }
  };

  return (
    <div className="page">
      <div className="container">
        <h1>Manage Users</h1>
        <p className="subtitle">{total} user{total !== 1 ? "s" : ""}</p>

        <div className="filter-bar">
          <select
            value={roleFilter}
            onChange={(e) => { setRoleFilter(e.target.value); setPage(1); }}
          >
            <option value="">All Roles</option>
            <option value="customer">Customers</option>
            <option value="seller">Sellers</option>
            <option value="admin">Admins</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Blocked</option>
          </select>
        </div>

        {loading ? <Loading /> : (
          <div className="admin-table">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Verified</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users
                  .filter((u) => !statusFilter || (statusFilter === "active" ? u.is_active : !u.is_active))
                  .map((u) => (
                  <tr key={u.id}>
                    <td><Link to={`/admin/users/${u.id}`}>{u.name}</Link></td>
                    <td>{u.email}</td>
                    <td><span className={`badge badge-${u.role}`}>{u.role}</span></td>
                    <td>
                      <span className={`badge ${u.is_active ? "badge-active" : "badge-inactive"}`}>
                        {u.is_active ? "Active" : "Blocked"}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${u.email_verified ? "badge-active" : "badge-pending"}`}>
                        {u.email_verified ? "Verified" : "Unverified"}
                      </span>
                    </td>
                    <td>
                      <div className="admin-table-actions">
                        <Link to={`/admin/users/${u.id}`} className="btn btn-outline btn-sm">View</Link>
                        <button
                          className={`btn btn-sm ${u.is_active ? "btn-danger-text" : "btn-outline"}`}
                          onClick={() => toggleStatus(u)}
                        >
                          {u.is_active ? "Block" : "Activate"}
                        </button>
                        <button
                          className="btn btn-outline btn-sm"
                          onClick={() => setConfirmReset(u)}
                        >
                          Reset PW
                        </button>
                        <button
                          className="btn btn-outline btn-sm"
                          onClick={() => { setRoleTarget(u); setRoleValue(u.role); }}
                        >
                          Role
                        </button>
                        {!u.email_verified && (
                          <button
                            className="btn btn-outline btn-sm"
                            onClick={() => setConfirmVerify(u)}
                          >
                            Verify Email
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {totalPages > 1 && (
          <div className="pagination">
            <button className="btn btn-outline btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
            <span className="pagination-info">Page {page} of {totalPages}</span>
            <button className="btn btn-outline btn-sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</button>
          </div>
        )}
      </div>

      <ConfirmDialog
        open={!!confirmReset}
        title="Reset this user's password?"
        message="The user's current password will be invalidated. A new strong password will be generated and shown to you ONCE."
        confirmLabel="Reset password"
        onConfirm={doReset}
        onCancel={() => setConfirmReset(null)}
      />

      <ConfirmDialog
        open={!!roleTarget}
        title={`Change role for ${roleTarget?.name || ""}?`}
        message="Granting admin gives full access. Choose carefully."
        confirmLabel="Update role"
        onConfirm={doChangeRole}
        onCancel={() => setRoleTarget(null)}
      >
        {roleTarget && (
          <div className="form-group" style={{ marginTop: 12 }}>
            <label>New role</label>
            <select value={roleValue} onChange={(e) => setRoleValue(e.target.value)}>
              <option value="customer">Customer</option>
              <option value="seller">Seller</option>
              <option value="admin">Admin</option>
            </select>
          </div>
        )}
      </ConfirmDialog>

      <ConfirmDialog
        open={!!confirmVerify}
        title="Mark email as verified?"
        message={`Manually mark ${confirmVerify?.email} as verified?`}
        confirmLabel="Verify"
        onConfirm={doVerifyEmail}
        onCancel={() => setConfirmVerify(null)}
      />

      {resetResult && (
        <div className="modal-backdrop" onClick={() => setResetResult(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>New password generated</h3>
              <button className="modal-close" onClick={() => setResetResult(null)} aria-label="Close">×</button>
            </div>
            <div className="modal-body">
              <p>Share this password securely with <strong>{resetResult.email}</strong>. It will not be shown again.</p>
              <div className="dash-coupon-code-row" style={{ marginTop: 12 }}>
                <code className="dash-coupon-code">{resetResult.new_password}</code>
                <button
                  className="btn btn-outline btn-sm"
                  onClick={() => navigator.clipboard?.writeText(resetResult.new_password)}
                >
                  Copy
                </button>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-primary" onClick={() => setResetResult(null)}>Done</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
