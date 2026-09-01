import { Link } from "react-router-dom";
import { useCart } from "../context/CartContext";
import Loading from "../components/Loading";

export default function Cart() {
  const { cart, loading, updateQuantity, removeFromCart, clearCart } = useCart();

  if (loading) return <Loading />;

  if (!cart.items || cart.items.length === 0) {
    return (
      <div className="page">
        <div className="container">
          <h1>Shopping Cart</h1>
          <div className="empty-state">
            <p>Your cart is empty.</p>
            <Link to="/" className="btn btn-primary" style={{ marginTop: 16 }}>
              Browse Products
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <h1>Shopping Cart</h1>
        <p className="subtitle">{cart.item_count} item{cart.item_count !== 1 ? "s" : ""} in your cart</p>

        <div className="cart-layout">
          <div className="cart-items">
            {cart.items.map((item) => (
              <div key={item.product_id} className="cart-item">
                <div className="cart-item-image">
                  <img
                    src={item.image_url || "/placeholder.png"}
                    alt={item.product_name}
                    onError={(e) => {
                      if (e.currentTarget.src !== window.location.origin + "/placeholder.png") {
                        e.currentTarget.src = "/placeholder.png";
                      }
                    }}
                  />
                </div>
                <div className="cart-item-info">
                  <Link to={`/products/${item.product_id}`} className="cart-item-name">
                    {item.product_name}
                  </Link>
                  <p className="cart-item-price">৳{item.price.toFixed(2)}</p>
                  <div className="cart-item-quantity">
                    <button
                      className="btn btn-outline btn-sm"
                      onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                      disabled={item.quantity <= 1}
                    >
                      -
                    </button>
                    <span className="cart-item-qty-value">{item.quantity}</span>
                    <button
                      className="btn btn-outline btn-sm"
                      onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                      disabled={item.quantity >= item.stock}
                    >
                      +
                    </button>
                  </div>
                  {item.quantity >= item.stock && (
                    <p className="cart-item-max">Max available: {item.stock}</p>
                  )}
                </div>
                <div className="cart-item-actions">
                  <p className="cart-item-subtotal">৳{item.subtotal.toFixed(2)}</p>
                  <button
                    className="btn btn-outline btn-sm btn-danger-text"
                    onClick={() => removeFromCart(item.product_id)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="cart-summary">
            <h3>Order Summary</h3>
            <div className="cart-summary-row">
              <span>Subtotal ({cart.item_count} items)</span>
              <span>৳{cart.total.toFixed(2)}</span>
            </div>
            <div className="cart-summary-row cart-summary-total">
              <span>Total</span>
              <span>৳{cart.total.toFixed(2)}</span>
            </div>
            <Link to="/checkout" className="btn btn-primary btn-full">
              Proceed to Checkout
            </Link>
            <button className="btn btn-outline btn-full" style={{ marginTop: 8 }} onClick={clearCart}>
              Clear Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
