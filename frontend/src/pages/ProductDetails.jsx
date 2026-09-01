import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import ErrorMessage from "../components/ErrorMessage";
import Loading from "../components/Loading";
import StarRating from "../components/StarRating";

const formatDate = (v) => {
  if (!v) return "";
  const d = new Date(v);
  return isNaN(d) ? "" : d.toLocaleDateString();
};

export default function ProductDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { addToCart } = useCart();
  const toast = useToast();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);
  const [reviews, setReviews] = useState([]);
  const [reviewForm, setReviewForm] = useState({ rating: 5, title: "", body: "" });
  const [submitting, setSubmitting] = useState(false);
  const [canReview, setCanReview] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get(`/products/${id}`);
        setProduct(res.data);
      } catch (err) {
        setError(err.response?.data?.detail || "Product not found.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  useEffect(() => {
    if (!id) return;
    api.get(`/products/${id}/reviews`)
      .then((r) => setReviews(Array.isArray(r.data) ? r.data : []))
      .catch(() => setReviews([]));
  }, [id]);

  useEffect(() => {
    if (!user || user.role !== "customer" || !id) {
      setCanReview(false);
      return;
    }
    // Best-effort: show the form. The server enforces the "must have purchased"
    // rule and returns a clear error if not.
    setCanReview(true);
  }, [user, id]);

  const handleAddToCart = async () => {
    if (!user || user.role !== "customer") return;
    setAdding(true);
    try {
      await addToCart(product.id, quantity);
      setAdded(true);
      setTimeout(() => setAdded(false), 2000);
    } catch {
      // error handled by context
    } finally {
      setAdding(false);
    }
  };

  const submitReview = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post(`/products/${id}/reviews`, reviewForm);
      toast.success("Thanks! Your review has been posted.");
      setReviewForm({ rating: 5, title: "", body: "" });
      const r = await api.get(`/products/${id}/reviews`);
      setReviews(Array.isArray(r.data) ? r.data : []);
      // Refresh the product so the average updates.
      const p = await api.get(`/products/${id}`);
      setProduct(p.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to submit review.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loading />;
  if (error) {
    return (
      <div className="page">
        <div className="container"><ErrorMessage message={error} /></div>
      </div>
    );
  }
  if (!product) return null;

  const price = typeof product.price === "number" ? product.price.toFixed(2) : "0.00";
  const companyName = product.company_name || "";
  const imageUrl = product.image_url || "/placeholder.png";
  const inStock = product.stock > 0;
  const avg = Number(product.avg_rating || 0);
  const count = Number(product.review_count || 0);

  return (
    <div className="page">
      <div className="container">
        <button className="btn btn-outline btn-back" onClick={() => navigate(-1)}>
          &larr; Back
        </button>
        <div className="product-details">
          <div className="product-details-image">
            <img
              src={imageUrl}
              alt={product.name}
              onError={(e) => {
                if (e.currentTarget.src !== "/placeholder.png") {
                  e.currentTarget.src = "/placeholder.png";
                }
              }}
            />
          </div>
          <div className="product-details-info">
            <h1>{product.name}</h1>
            {companyName && (
              <p className="product-details-company">by {companyName}</p>
            )}
            <div className="product-details-rating">
              <StarRating value={avg} count={count} size={18} />
            </div>
            <p className="product-details-price">৳{price}</p>
            <p className="product-details-stock">
              {inStock ? `${product.stock} in stock` : "Out of stock"}
            </p>
            {product.description && (
              <div className="product-details-description">
                <h3>Description</h3>
                <p>{product.description}</p>
              </div>
            )}
            {user && user.role === "customer" && inStock && (
              <div className="product-details-cart">
                <div className="quantity-selector">
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    disabled={quantity <= 1}
                  >
                    -
                  </button>
                  <span className="quantity-value">{quantity}</span>
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                    disabled={quantity >= product.stock}
                  >
                    +
                  </button>
                </div>
                <button
                  className="btn btn-primary"
                  onClick={handleAddToCart}
                  disabled={adding}
                >
                  {added ? "Added!" : adding ? "Adding..." : "Add to Cart"}
                </button>
              </div>
            )}
            {(!user || user.role !== "customer") && inStock && (
              <p className="product-details-login-hint">
                <a href="/login">Log in</a> as a customer to add to cart.
              </p>
            )}
          </div>
        </div>

        <section className="product-reviews">
          <h2>Customer reviews</h2>
          {reviews.length === 0 ? (
            <p className="dash-muted">No reviews yet. Be the first to review this product.</p>
          ) : (
            <ul className="product-reviews-list">
              {reviews.map((r) => (
                <li key={r.id} className="product-review">
                  <div className="product-review-head">
                    <strong>{r.user_name || "Customer"}</strong>
                    <StarRating value={r.rating} count={0} size={14} />
                    <span className="dash-muted" style={{ fontSize: 12 }}>
                      {formatDate(r.created_at)}
                    </span>
                  </div>
                  {r.title && <div className="product-review-title">{r.title}</div>}
                  {r.body && <p className="product-review-body">{r.body}</p>}
                </li>
              ))}
            </ul>
          )}

          {canReview && (
            <form className="product-review-form" onSubmit={submitReview}>
              <h3>Write a review</h3>
              <p className="dash-muted" style={{ marginBottom: 12 }}>
                You can only review products you have purchased.
              </p>
              <div className="form-row">
                <div className="form-group">
                  <label>Rating</label>
                  <select
                    value={reviewForm.rating}
                    onChange={(e) =>
                      setReviewForm({ ...reviewForm, rating: Number(e.target.value) })
                    }
                  >
                    <option value={5}>5 — Excellent</option>
                    <option value={4}>4 — Very good</option>
                    <option value={3}>3 — Good</option>
                    <option value={2}>2 — Fair</option>
                    <option value={1}>1 — Poor</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Title (optional)</label>
                <input
                  type="text"
                  maxLength={120}
                  value={reviewForm.title}
                  onChange={(e) => setReviewForm({ ...reviewForm, title: e.target.value })}
                  placeholder="Sum it up in a few words"
                />
              </div>
              <div className="form-group">
                <label>Review</label>
                <textarea
                  rows={4}
                  maxLength={2000}
                  value={reviewForm.body}
                  onChange={(e) => setReviewForm({ ...reviewForm, body: e.target.value })}
                  placeholder="What did you like or dislike?"
                />
              </div>
              <button className="btn btn-primary" type="submit" disabled={submitting}>
                {submitting ? "Submitting…" : "Post review"}
              </button>
            </form>
          )}
        </section>
      </div>
    </div>
  );
}
