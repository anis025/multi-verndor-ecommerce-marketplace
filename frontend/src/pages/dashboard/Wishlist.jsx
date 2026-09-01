import { useEffect, useState } from "react";
import { wishlistService } from "../../services/wishlistService";
import { Skeleton } from "../../components/dashboard/Skeleton";
import EmptyState from "../../components/dashboard/EmptyState";
import ConfirmDialog from "../../components/dashboard/ConfirmDialog";
import { useToast } from "../../context/ToastContext";
import { IconHeart, IconCart, IconTrash } from "../../components/dashboard/Icon";

export default function Wishlist() {
  const toast = useToast();
  const [items, setItems] = useState(null);
  const [error, setError] = useState(null);
  const [confirm, setConfirm] = useState(null);

  useEffect(() => {
    setError(null);
    wishlistService
      .list()
      .then(setItems)
      .catch(() => {
        setError("Could not load wishlist.");
        setItems([]);
      });
  }, []);

  const handleRemove = async () => {
    const id = confirm;
    setConfirm(null);
    try {
      await wishlistService.remove(id);
      setItems((arr) => arr.filter((w) => w.id !== id));
      toast.success("Removed from wishlist.");
    } catch {
      toast.error("Failed to remove item.");
    }
  };

  const handleAddToCart = async (item) => {
    try {
      await wishlistService.addToCart(item.product_id);
      toast.success(`"${item.name}" added to cart.`);
    } catch {
      toast.error("Failed to add to cart.");
    }
  };

  if (items === null) {
    return (
      <div className="dash-page">
        <h1>Wishlist</h1>
        <div className="dash-grid-cards">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="dash-product-card">
              <Skeleton height={180} radius={12} />
              <Skeleton height={16} width="80%" style={{ marginTop: 12 }} />
              <Skeleton height={16} width="40%" style={{ marginTop: 8 }} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="dash-page">
      <header className="dash-page-header">
        <div>
          <h1>Wishlist</h1>
          <p className="dash-muted">{items.length} item{items.length !== 1 ? "s" : ""} saved for later.</p>
        </div>
      </header>

      {error && <div className="alert alert-error">{error}</div>}

      {items.length === 0 ? (
        <EmptyState
          icon={IconHeart}
          title="Your wishlist is empty"
          description="Save products you love and come back to them anytime."
          actionLabel="Discover Products"
          actionTo="/"
        />
      ) : (
        <div className="dash-grid-cards">
          {items.map((it) => (
            <article key={it.id} className="dash-product-card">
              <div className="dash-product-image">
                <img src={it.image_url} alt={it.name} loading="lazy" />
                {it.discount_percent > 0 && (
                  <span className="dash-badge-discount">-{it.discount_percent}%</span>
                )}
              </div>
              <div className="dash-product-body">
                <h3 className="dash-product-title">{it.name}</h3>
                <div className="dash-product-price-row">
                  <span className="dash-product-price">৳{it.price.toFixed(2)}</span>
                  {it.discount_percent > 0 && (
                    <span className="dash-product-was">
                      ৳{(it.price / (1 - it.discount_percent / 100)).toFixed(2)}
                    </span>
                  )}
                </div>
                <div className={`dash-stock ${it.in_stock ? "in" : "out"}`}>
                  {it.in_stock ? `In stock · ${it.stock} left` : "Out of stock"}
                </div>
                <div className="dash-product-actions">
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => handleAddToCart(it)}
                    disabled={!it.in_stock}
                  >
                    <IconCart size={14} /> Add to Cart
                  </button>
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => setConfirm(it.id)}
                    aria-label="Remove from wishlist"
                  >
                    <IconTrash size={14} />
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={!!confirm}
        title="Remove from wishlist?"
        message="This item will be removed from your saved list."
        confirmLabel="Remove"
        onConfirm={handleRemove}
        onCancel={() => setConfirm(null)}
      />
    </div>
  );
}
