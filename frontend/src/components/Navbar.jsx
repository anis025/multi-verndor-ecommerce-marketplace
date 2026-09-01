import { useState, useEffect } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import api from "../services/api";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { cart } = useCart();
  const cartCount = cart?.item_count || 0;
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [query, setQuery] = useState(searchParams.get("search") || "");
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState(searchParams.get("category") || "");

  useEffect(() => {
    api.get("/categories/active")
      .then((res) => setCategories(res.data.items || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setQuery(searchParams.get("search") || "");
    setCategory(searchParams.get("category") || "");
  }, [searchParams]);

  const handleSearch = (e) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (query.trim()) params.set("search", query.trim());
    if (category) params.set("category", category);
    navigate(`/?${params.toString()}`);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">Hatify</Link>

        <form className="navbar-search" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Search products..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="navbar-search-input"
          />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="navbar-search-select"
          >
            <option value="">All</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.name}>{cat.name}</option>
            ))}
          </select>
          <button type="submit" className="btn-search">Search</button>
        </form>

        <div className="navbar-links">
          {user ? (
            <>
              {user.role === "customer" && (
                <>
                  <Link to="/cart" className="cart-link">
                    Cart
                    {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
                  </Link>
                  <Link to="/dashboard">My Account</Link>
                </>
              )}
              {user.role === "seller" && <Link to="/seller">Seller Dashboard</Link>}
              {user.role === "admin" && <Link to="/admin">Admin Dashboard</Link>}
              <Link to="/profile">{user.name || user.email}</Link>
              <button className="btn btn-outline" onClick={logout}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-login">Login</Link>
              <Link to="/register" className="btn btn-register">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
