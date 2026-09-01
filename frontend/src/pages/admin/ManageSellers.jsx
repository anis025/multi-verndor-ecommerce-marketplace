import { useState, useEffect } from "react";
import api from "../../services/api";
import Loading from "../../components/Loading";

export default function ManageSellers() {
  const [sellers, setSellers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState("");

  const [modal, setModal] = useState(null);
  const [reason, setReason] = useState("");

  const fetchSellers = async (p) => {
    setLoading(true);
    try {
      const params = { page: p, limit: 10 };
      if (statusFilter) params.status = statusFilter;
      const res = await api.get("/admin/sellers", { params });
      setSellers(res.data.items);
      setTotalPages(res.data.total_pages || Math.ceil(res.data.total / 10));
      setTotal(res.data.total);
    } catch {
      setSellers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchSellers(page); }, [page, statusFilter]);

  const applyStatus = async (sellerId, status, reasonText) => {
    await api.patch(`/admin/sellers/${sellerId}/status`, { status, reason: reasonText || undefined });
    fetchSellers(page);
  };

  const confirmModal = async () => {
    if (!modal) return;
    if ((modal.action === "rejected" || modal.action === "suspended") && !reason.trim()) return;
    await applyStatus(modal.sellerId, modal.action, reason);
    setModal(null);
    setReason("");
  };

  const openAction = (s, action) => {
    if (action === "rejected" || action === "suspended") {
      setModal({
        sellerId: s.id,
        sellerName: s.company_name,
        action,
        title: action === "rejected" ? "Reject Seller" : "Suspend Seller",
      });
    } else {
      applyStatus(s.id, action, "");
    }
  };

  const actionsFor = (s) => {
    switch (s.status) {
      case "pending":
        return [
          <button key="a" className="btn btn-outline btn-sm" onClick={() => openAction(s, "approved")}>Approve</button>,
          <button key="r" className="btn btn-outline btn-sm btn-danger-text" onClick={() => openAction(s, "rejected")}>Reject</button>,
        ];
      case "approved":
        return [
          <button key="s" className="btn btn-outline btn-sm btn-danger-text" onClick={() => openAction(s, "suspended")}>Suspend</button>,
        ];
      case "suspended":
        return [
          <button key="r" className="btn btn-outline btn-sm" onClick={() => openAction(s, "approved")}>Reactivate</button>,
        ];
      case "rejected":
        return [
          <button key="o" className="btn btn-outline btn-sm" onClick={() => openAction(s, "pending")}>Reopen</button>,
        ];
      default:
        return null;
    }
  };

  return (
    <div className="page">
      <div className="container">
        <h1>Manage Sellers</h1>
        <p className="subtitle">{total} seller{total !== 1 ? "s" : ""}</p>

        <div className="filter-bar">
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="suspended">Suspended</option>
          </select>
        </div>

        {loading ? <Loading /> : (
          <div className="admin-table">
            <table>
              <thead>
                <tr>
                  <th>Store</th>
                  <th>Owner</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sellers.map((s) => (
                  <tr key={s.id}>
                    <td>{s.company_name}</td>
                    <td>{s.user_name}</td>
                    <td>{s.user_email}</td>
                    <td><span className={`badge badge-${s.status}`}>{s.status}</span></td>
                    <td className="actions-cell">{actionsFor(s)}</td>
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

        {modal && (
          <div className="modal-overlay" onClick={() => setModal(null)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h3>{modal.title}</h3>
              <p>Store: <strong>{modal.sellerName}</strong></p>
              <div className="form-group">
                <label>Reason {modal.action === "rejected" ? "(required)" : ""}</label>
                <textarea value={reason} onChange={(e) => setReason(e.target.value)} rows={3} placeholder="Optional explanation..." />
              </div>
              <div className="modal-actions">
                <button className="btn btn-outline" onClick={() => setModal(null)}>Cancel</button>
                <button className="btn btn-primary" onClick={confirmModal}>Confirm</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
