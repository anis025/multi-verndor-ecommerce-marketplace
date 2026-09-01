import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useCart } from "../../context/CartContext";
import { useToast } from "../../context/ToastContext";
import { Skeleton } from "../../components/dashboard/Skeleton";
import EmptyState from "../../components/dashboard/EmptyState";
import { IconCart, IconTag, IconTrash } from "../../components/dashboard/Icon";

export default function CartPage() {
  const { cart, loading, updateQuantity, removeFromCart, clearCart } = useCart();
  const toast = useToast();
  const [coupon, setCoupon] = useState("");
  const [appliedCoupon, setAppliedCoupon] = useState(null);

  useEffect(() => {
    setCoupon(appliedCoupon?.code || "");
  }, [appliedCoupon]);

  if (loading) {
    return (
      <div className="dash-page">
        <h1>Cart</h1>
        <div className="dash-card">
          <Skeleton height={80} style={{ marginBottom: 12 }} />
          <Skeleton height={80} style={{ marginBottom: 12 }} />
          <Skeleton height={80} />
        </div>
      </div>
    );
  }

  const items = cart?.items || [];
  const subtotal = cart?.total || 0;
  const discount = appliedCoupon
    ? appliedCoupon.discount_type === "percent"
      ? (subtotal * appliedCoupon.discount_value) / 100
      : appliedCoupon.discount_type === "fixed"
      ? Math.min(appliedCoupon.discount_value, subtotal)
      : 0
    : 0;
  const shipping = subtotal > 0 ? 0 : 0;
  const total = Math.max(0, subtotal - discount + shipping);

  const applyCoupon = (e) => {
    e.preventDefault();
    const code = coupon.trim().toUpperCase();
    if (!code) return;
    // Demo: a couple of known codes
    if (code === "WELCOME10") setAppliedCoupon({ code, discount_type: "percent", discount_value: 10 });
    else if (code === "SAVE20") setAppliedCoupon({ code, discount_type: "fixed", discount_value: 20 });
    else {
      toast.error("Invalid coupon code.");
      return;
    }
    toast.success("Coupon applied.");
  };

  const handleRemove = async (id) => {
    try {
      await removeFromCart(id);
      toast.info("Item removed from cart.");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to remove item.");
    }
  };

  const handleClear = async () => {
    try {
      await clearCart();
      setAppliedCoupon(null);
      toast.info("Cart cleared.");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to clear cart.");
    }
  };

  return (
    <div className="dash-page">
      <header className="dash-page-header">
        <div>
          <h1>My Cart</h1>
          <p className="dash-muted">{cart?.item_count || 0} item{cart?.item_count !== 1 ? "s" : ""} in your cart</p>
        </div>
        {items.length > 0 && (
          <button className="btn btn-outline" onClick={handleClear}>Clear Cart</button>
        )}
      </header>

      {items.length === 0 ? (
        <EmptyState
          icon={IconCart}
          title="Your cart is empty"
          description="Add some products to checkout."
          actionLabel="Browse Products"
          actionTo="/"
        />
      ) : (
        <div className="dash-cart-layout">
          <div className="dash-cart-items">
            {items.map((it) => (
              <div key={it.product_id} className="dash-cart-item">
                <div className="dash-cart-image">
                  <img src={it.image_url || "/placeholder.png"} alt={it.product_name} />
                </div>
                <div className="dash-cart-info">
                  <Link to={`/products/${it.product_id}`} className="dash-cart-name">
                    {it.product_name}
                  </Link>
                  <div className="dash-muted">৳{it.price.toFixed(2)} each</div>
                  <div className="dash-qty">
                    <button
                      className="btn btn-outline btn-sm"
                      onClick={() => updateQuantity(it.product_id, it.quantity - 1)}
                      disabled={it.quantity <= 1}
                    >−</button>
                    <span>{it.quantity}</span>
                    <button
                      className="btn btn-outline btn-sm"
                      onClick={() => updateQuantity(it.product_id, it.quantity + 1)}
                      disabled={it.quantity >= it.stock}
                    >+</button>
                  </div>
                </div>
                <div className="dash-cart-right">
                  <div className="dash-strong">৳{it.subtotal.toFixed(2)}</div>
                  <button
                    className="btn-link dash-danger"
                    onClick={() => handleRemove(it.product_id)}
                  >
                    <IconTrash size={14} /> Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          <aside className="dash-card dash-cart-summary">
            <h2 className="dash-section-title">Order Summary</h2>
            <form className="dash-coupon" onSubmit={applyCoupon}>
              <IconTag size={16} />
              <input
                type="text"
                value={coupon}
                onChange={(e) => setCoupon(e.target.value)}
                placeholder="Enter coupon code"
                aria-label="Coupon code"
              />
              <button className="btn btn-outline btn-sm" type="submit">Apply</button>
            </form>
            {appliedCoupon && (
              <div className="dash-applied-coupon">
                <span><IconTag size={14} /> <strong>{appliedCoupon.code}</strong> applied</span>
                <button className="btn-link" onClick={() => setAppliedCoupon(null)}>Remove</button>
              </div>
            )}

            <div className="dash-price-row"><span>Subtotal</span><span>৳{subtotal.toFixed(2)}</span></div>
            <div className="dash-price-row">
              <span>Discount</span>
              <span>{discount ? `-৳${discount.toFixed(2)}` : "—"}</span>
            </div>
            <div className="dash-price-row"><span>Shipping</span><span>{shipping ? `৳${shipping.toFixed(2)}` : "Free"}</span></div>
            <div className="dash-price-row dash-price-total"><span>Total</span><span>৳{total.toFixed(2)}</span></div>

            <Link to="/checkout" className="btn btn-primary btn-full">
              Proceed to Checkout
            </Link>
          </aside>
        </div>
      )}
    </div>
  );
}
