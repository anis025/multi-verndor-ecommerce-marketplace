import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../services/api";
import HeroSlider from "../components/HeroSlider";
import ProductGrid from "../components/ProductGrid";
import ErrorMessage from "../components/ErrorMessage";

export default function Home() {
  const [searchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const search = searchParams.get("search") || "";
  const category = searchParams.get("category") || "";

  const fetchProducts = async (pageNum = 1) => {
    setError(null);
    try {
      const params = { page: pageNum, limit: 12 };
      if (search) params.search = search;
      if (category) params.category = category;
      const res = await api.get("/products", { params });
      setProducts(res.data.items || res.data.products || []);
      setTotalPages(res.data.total_pages || 1);
      setTotal(res.data.total || 0);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load products.");
    }
  };

  useEffect(() => {
    setPage(1);
    fetchProducts(1);
  }, [search, category]);

  const handlePageChange = (newPage) => {
    setPage(newPage);
    fetchProducts(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const isSearching = search || category;

  return (
    <div>
      {!isSearching && <HeroSlider />}

      <div className="page">
        <div className="container">
          {isSearching && (
            <div className="search-results-header">
              <h2>
                {search && <span>Results for &ldquo;{search}&rdquo;</span>}
                {search && category && <span> in </span>}
                {category && <span>{category}</span>}
              </h2>
              <p className="subtitle">
                {total} product{total !== 1 ? "s" : ""} found
              </p>
            </div>
          )}

          {!isSearching && (
            <>
              <h2 className="section-title">All Products</h2>
              <p className="subtitle">Browse our collection</p>
            </>
          )}

          {error ? (
            <ErrorMessage
              message={error}
              onRetry={() => fetchProducts(page)}
            />
          ) : (
            <>
              <ProductGrid
                products={products}
                emptyMessage="No products available yet."
              />
              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    className="btn btn-outline"
                    disabled={page <= 1}
                    onClick={() => handlePageChange(page - 1)}
                  >
                    Previous
                  </button>
                  <span className="pagination-info">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    className="btn btn-outline"
                    disabled={page >= totalPages}
                    onClick={() => handlePageChange(page + 1)}
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
