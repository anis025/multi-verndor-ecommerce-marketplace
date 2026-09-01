import { useEffect, useState } from "react";
import { couponService } from "../../services/couponService";
import { useToast } from "../../context/ToastContext";
import { Skeleton } from "../../components/dashboard/Skeleton";
import EmptyState from "../../components/dashboard/EmptyState";
import { IconTag, IconCopy, IconCheck } from "../../components/dashboard/Icon";

const formatDiscount = (c) => {
  if (c.discount_type === "percent") return `${c.discount_value}% off`;
  if (c.discount_type === "fixed") return `৳${c.discount_value} off`;
  if (c.discount_type === "shipping") return "Free shipping";
  return "Discount";
};

const formatDate = (iso) => {
  if (!iso) return "";
  const d = new Date(iso);
  return isNaN(d) ? "" : d.toLocaleDateString();
};

export default function Coupons() {
  const toast = useToast();
  const [items, setItems] = useState(null);
  const [copied, setCopied] = useState(null);

  useEffect(() => {
    couponService.list().then(setItems).catch(() => setItems([]));
  }, []);

  const handleCopy = async (code) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(code);
      toast.success(`Copied "${code}" to clipboard.`);
      setTimeout(() => setCopied((c) => (c === code ? null : c)), 1500);
    } catch {
      toast.error("Couldn't copy. Please copy manually.");
    }
  };

  if (items === null) {
    return (
      <div className="dash-page">
        <h1>Coupons & Offers</h1>
        <div className="dash-grid-cards">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="dash-card"><Skeleton height={20} width="60%" /></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="dash-page">
      <header className="dash-page-header">
        <div>
          <h1>Coupons & Offers</h1>
          <p className="dash-muted">Save more on your next purchase.</p>
        </div>
      </header>

      {items.length === 0 ? (
        <EmptyState
          icon={IconTag}
          title="No coupons available"
          description="Check back later for new offers."
        />
      ) : (
        <div className="dash-grid-cards">
          {items.map((c) => (
            <article key={c.id} className={"dash-card dash-coupon-card" + (c.status === "expired" ? " dash-coupon-expired" : "")}>
              <div className="dash-coupon-head">
                <IconTag size={18} />
                <div className="dash-coupon-value">{formatDiscount(c)}</div>
              </div>
              <h3 className="dash-coupon-title">{c.title}</h3>
              <p className="dash-muted">{c.description}</p>
              <ul className="dash-coupon-meta">
                <li>Min spend: ৳{c.min_spend.toFixed(2)}</li>
                <li>Expires: {formatDate(c.expires_at)}</li>
                {c.status === "expired" && <li className="dash-coupon-status">Expired</li>}
              </ul>
              <div className="dash-coupon-code-row">
                <code className="dash-coupon-code">{c.code}</code>
                <button
                  className="btn btn-outline btn-sm"
                  onClick={() => handleCopy(c.code)}
                  disabled={c.status === "expired"}
                >
                  {copied === c.code ? <><IconCheck size={14} /> Copied</> : <><IconCopy size={14} /> Copy Code</>}
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
