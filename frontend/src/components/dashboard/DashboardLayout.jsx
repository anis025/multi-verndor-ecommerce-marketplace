import { useEffect, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useToast } from "../../context/ToastContext";
import { notificationService } from "../../services/notificationService";
import {
  IconBell,
  IconBox,
  IconCard,
  IconCart,
  IconChevronRight,
  IconHeart,
  IconHome,
  IconLock,
  IconLogout,
  IconMapPin,
  IconMenu,
  IconTag,
  IconUser,
  IconX,
} from "./Icon";

const NAV = [
  { to: "/dashboard", label: "Overview", icon: IconHome, end: true },
  { to: "/dashboard/orders", label: "My Orders", icon: IconBox },
  { to: "/dashboard/wishlist", label: "Wishlist", icon: IconHeart },
  { to: "/dashboard/cart", label: "Cart", icon: IconCart },
  { to: "/dashboard/profile", label: "Profile", icon: IconUser },
  { to: "/dashboard/password", label: "Password", icon: IconLock },
  { to: "/dashboard/addresses", label: "Address Book", icon: IconMapPin },
  { to: "/dashboard/payments", label: "Payment Methods", icon: IconCard },
  { to: "/dashboard/notifications", label: "Notifications", icon: IconBell, badgeKey: "unread" },
  { to: "/dashboard/coupons", label: "Coupons & Offers", icon: IconTag },
];

export default function DashboardLayout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    notificationService.unreadCount().then(setUnread).catch(() => {});
  }, [location.pathname]);

  useEffect(() => {
    setDrawerOpen(false);
  }, [location.pathname]);

  const handleLogout = async () => {
    try {
      await logout();
    } catch {
      // ignore network errors; still clear local session
    }
    toast.success("You've been logged out.");
    // Force a navigation that replaces history so back button cannot return
    // to a protected dashboard page.
    navigate("/login", { replace: true, state: { from: "logout" } });
  };

  const initials = (user?.name || user?.email || "U")
    .split(/\s+/)
    .map((s) => s[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();

  const sidebar = (
    <aside className="dash-sidebar">
      <div className="dash-brand">
        <span className="dash-brand-mark">H</span>
        <span className="dash-brand-text">Hatify</span>
      </div>

      <div className="dash-user">
        <div className="dash-avatar">{initials || "U"}</div>
        <div>
          <div className="dash-user-name">{user?.name || "Customer"}</div>
          <div className="dash-user-email">{user?.email}</div>
        </div>
      </div>

      <nav className="dash-nav" aria-label="Dashboard navigation">
        {NAV.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                "dash-nav-link" + (isActive ? " dash-nav-link-active" : "")
              }
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {item.badgeKey === "unread" && unread > 0 && (
                <span className="dash-nav-badge" aria-label={`${unread} unread`}>
                  {unread}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      <button className="dash-logout" onClick={handleLogout}>
        <IconLogout size={18} />
        <span>Logout</span>
      </button>
    </aside>
  );

  return (
    <div className="dash-shell">
      <button
        className="dash-mobile-toggle"
        onClick={() => setDrawerOpen(true)}
        aria-label="Open navigation"
      >
        <IconMenu size={22} />
      </button>

      {sidebar}

      {drawerOpen && (
        <div className="dash-drawer-backdrop" onClick={() => setDrawerOpen(false)}>
          <div className="dash-drawer" onClick={(e) => e.stopPropagation()}>
            <button
              className="dash-drawer-close"
              onClick={() => setDrawerOpen(false)}
              aria-label="Close navigation"
            >
              <IconX size={20} />
            </button>
            {sidebar}
          </div>
        </div>
      )}

      <main className="dash-main">
        <div className="dash-content">{children}</div>
      </main>
    </div>
  );
}
