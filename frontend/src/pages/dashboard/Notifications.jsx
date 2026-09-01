import { useEffect, useState } from "react";
import { notificationService } from "../../services/notificationService";
import { useToast } from "../../context/ToastContext";
import { Skeleton } from "../../components/dashboard/Skeleton";
import EmptyState from "../../components/dashboard/EmptyState";
import { IconBell, IconCheck, IconBox, IconTag, IconStar, IconTruck } from "../../components/dashboard/Icon";

const ICONS = {
  order: IconBox,
  coupon: IconTag,
  stock: IconStar,
  promo: IconTag,
};

const relative = (iso) => {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d)) return "";
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return d.toLocaleDateString();
};

export default function Notifications() {
  const toast = useToast();
  const [items, setItems] = useState(null);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    notificationService.list().then(setItems).catch(() => setItems([]));
  }, []);

  const handleMarkAll = async () => {
    try {
      await notificationService.markAllRead();
      setItems((arr) => arr.map((n) => ({ ...n, is_read: true })));
      toast.success("All notifications marked as read.");
    } catch {
      toast.error("Failed to mark notifications.");
    }
  };

  const handleMarkOne = async (id) => {
    try {
      await notificationService.markRead(id);
      setItems((arr) => arr.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    } catch {
      toast.error("Failed to mark notification.");
    }
  };

  if (items === null) {
    return (
      <div className="dash-page">
        <h1>Notifications</h1>
        <div className="dash-card">
          <Skeleton height={48} style={{ marginBottom: 8 }} />
          <Skeleton height={48} style={{ marginBottom: 8 }} />
          <Skeleton height={48} />
        </div>
      </div>
    );
  }

  const filtered = filter === "unread" ? items.filter((n) => !n.is_read) : items;
  const unreadCount = items.filter((n) => !n.is_read).length;

  return (
    <div className="dash-page">
      <header className="dash-page-header">
        <div>
          <h1>Notification Center</h1>
          <p className="dash-muted">{unreadCount} unread of {items.length} total.</p>
        </div>
        <div className="dash-toolbar-right">
          <select className="dash-select" value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="unread">Unread</option>
          </select>
          <button className="btn btn-outline" onClick={handleMarkAll} disabled={unreadCount === 0}>
            <IconCheck size={14} /> Mark all as read
          </button>
        </div>
      </header>

      {filtered.length === 0 ? (
        <EmptyState
          icon={IconBell}
          title={filter === "unread" ? "You're all caught up!" : "No notifications yet"}
          description={filter === "unread" ? "No unread items right now." : "We'll let you know when something happens."}
        />
      ) : (
        <section className="dash-card">
          <ul className="dash-notif-list">
            {filtered.map((n) => {
              const Icon = ICONS[n.type] || IconBell;
              return (
                <li
                  key={n.id}
                  className={"dash-notif" + (n.is_read ? "" : " dash-notif-unread")}
                  onClick={() => !n.is_read && handleMarkOne(n.id)}
                >
                  <div className="dash-notif-icon">
                    <Icon size={18} />
                  </div>
                  <div className="dash-notif-body">
                    <div className="dash-notif-title">{n.title}</div>
                    <div className="dash-notif-text">{n.body}</div>
                  </div>
                  <div className="dash-notif-time">{relative(n.created_at)}</div>
                  {!n.is_read && <span className="dash-notif-dot" aria-hidden="true" />}
                </li>
              );
            })}
          </ul>
        </section>
      )}
    </div>
  );
}
