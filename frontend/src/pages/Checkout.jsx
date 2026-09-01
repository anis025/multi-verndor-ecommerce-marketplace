import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import api from "../services/api";
import ErrorMessage from "../components/ErrorMessage";

export default function Checkout() {
  const navigate = useNavigate();
  const { cart, fetchCart } = useCart();
  const [form, setForm] = useState({ name: "", phone: "", address: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!form.name.trim() || !form.phone.trim() || !form.address.trim()) {
      setError("All fields are required.");
      return;
    }

    setLoading(true);
    try {
      const res = await api.post("/orders", {
        shipping_address: { name: form.name, phone: form.phone, address: form.address },
      });
      await fetchCart();
      navigate(`/orders/${res.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to place order.");
    } finally {
      setLoading(false);
    }
  };

  if (!cart.items || cart.items.length === 0) {
    return (
      <div className="page">
        <div className="container">
          <h1>Checkout</h1>
          <div className="empty-state">
            <p>Your cart is empty.</p>
            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => navigate("/")}>
              Browse Products
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <h1>Checkout</h1>
        <div className="checkout-layout">
          <form className="checkout-form" onSubmit={handleSubmit}>
            <h3>Shipping Address</h3>
            {error && <ErrorMessage message={error} />}
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text" id="name" name="name"
                value={form.name} onChange={handleChange}
                placeholder="John Doe" required
              />
            </div>
            <div className="form-group">
              <label htmlFor="phone">Phone Number</label>
              <input
                type="text" id="phone" name="phone"
                value={form.phone} onChange={handleChange}
                placeholder="01700000000" required
              />
            </div>
            <div className="form-group">
              <label htmlFor="address">Address</label>
              <textarea
                id="address" name="address" rows="3"
                value={form.address} onChange={handleChange}
                placeholder="Dhaka, Bangladesh" required
              />
            </div>
            <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
              {loading ? "Placing Order..." : "Place Order"}
            </button>
          </form>

          <div className="cart-summary">
            <h3>Order Summary</h3>
            {cart.items.map((item) => (
              <div key={item.product_id} className="checkout-item">
                <span>{item.product_name} x {item.quantity}</span>
                <span>৳{item.subtotal.toFixed(2)}</span>
              </div>
            ))}
            <div className="cart-summary-row cart-summary-total">
              <span>Total</span>
              <span>৳{cart.total.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
