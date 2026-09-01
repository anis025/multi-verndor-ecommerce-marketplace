import { Link } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import StarRating from "./StarRating";

export default function ProductCard({ product }) {
  const { user } = useAuth();
  const { addToCart } = useCart();

  const price = typeof product.price === "number" ? product.price.toFixed(2) : "0.00";
  const imageUrl = product.image_url || "/placeholder.png";
  const inStock = product.stock > 0;
  const companyName = product.company_name || "";
  const avg = Number(product.avg_rating || 0);
  const count = Number(product.review_count || 0);

  const handleAddToCart = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (user && user.role === "customer") {
      addToCart(product.id);
    }
  };

  return (
    <Link to={`/products/${product.id}`} className="product-card">
      <div className="product-card-image">
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
      <div className="product-card-info">
        <h3 className="product-card-name">{product.name}</h3>
        {companyName && (
          <p className="product-card-company" title={companyName}>
            {companyName}
          </p>
        )}
        <StarRating value={avg} count={count} size={14} />
        <p className="product-card-price">৳{price}</p>
        <p className="product-card-stock">
          {inStock ? `${product.stock} in stock` : "Out of stock"}
        </p>
        {user && user.role === "customer" && inStock && (
          <button className="btn btn-primary btn-sm btn-full" onClick={handleAddToCart}>
            Add to Cart
          </button>
        )}
      </div>
    </Link>
  );
}
