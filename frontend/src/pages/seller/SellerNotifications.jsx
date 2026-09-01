import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../../services/api";
import Loading from "../../components/Loading";

export default function SellerNotifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchNotifications = async (p) => {
    setLoading(true);
    try {
      const res = await api.get("/notifications", { params: { page: p, limit: 10 } });
      setNotifications(res.data.items);
      setTotalPages(res.data.total_pages);
      setUnreadCount(res.data.unread_count);
    } catch {
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchNotifications(page); }, [page]);

  const markRead = async (notifId) => {
    try {
      await api.put(`/notifications/${notifId}/read`);
      fetchNotifications(page);
    } catch {
      // silent
    }
  };

  const markAllRead = async () => {
    try {
      await api.put("/notifications/read-all");
      fetchNotifications(page);
    } catch {
      // silent
    }
  };

  if (loading && notifications.length === 0) return <Loading />;

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <h1>Notifications</h1>
          {unreadCount > 0 && (
            <button className="btn btn-outline" onClick={markAllRead}>Mark All as Read</button>
          )}
        </div>
        <p className="subtitle">{unreadCount} unread</p>

        {notifications.length === 0 ? (
          <div className="empty-state"><p>No notifications.</p></div>
        ) : (
          <div className="notifications-list">
            {notifications.map((n) => (
              <div key={n.id} className={`notification-card ${n.is_read ? "" : "unread"}`}>
                <div className="notification-content">
                  <strong>{n.title}</strong>
                  <p>{n.message}</p>
                  <span className="notification-date">{new Date(n.created_at).toLocaleDateString()}</span>
                </div>
                <div className="notification-actions">
                  {n.order_id && (
                    <Link to={`/seller/orders/${n.order_id}`} className="btn btn-outline btn-sm">View Order</Link>
                  )}
                  {!n.is_read && (
                    <button className="btn btn-outline btn-sm" onClick={() => markRead(n.id)}>Mark Read</button>
                  )}
                </div>
              </div>
            ))}
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
