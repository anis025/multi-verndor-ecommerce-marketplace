import { useState, useEffect } from "react";
import api from "../../services/api";
import Loading from "../../components/Loading";

export default function AuditLog() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchLogs = async (p) => {
    setLoading(true);
    try {
      const res = await api.get("/admin/audit-logs", { params: { page: p, limit: 15 } });
      setLogs(res.data.items);
      setTotalPages(Math.max(1, Math.ceil(res.data.total / 15)));
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLogs(page); }, [page]);

  return (
    <div className="page">
      <div className="container">
        <h1>Audit Log</h1>
        <p className="subtitle">Administrative actions</p>
        {loading ? <Loading /> : (
          <div className="admin-table">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Admin</th>
                  <th>Action</th>
                  <th>Target</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((l) => (
                  <tr key={l.id}>
                    <td>{new Date(l.created_at).toLocaleString()}</td>
                    <td>{l.admin_id}</td>
                    <td><span className="badge badge-active">{l.action}</span></td>
                    <td>{l.target_type}{l.target_id ? ":" + l.target_id.slice(0, 8) : ""}</td>
                    <td style={{ fontSize: 12 }}>{JSON.stringify(l.details)}</td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr><td colSpan={5} style={{ textAlign: "center", padding: 20 }}>No entries</td></tr>
                )}
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
    </div>
  );
}
