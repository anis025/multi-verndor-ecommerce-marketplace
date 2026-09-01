import { createContext, useContext, useState, useEffect, useCallback } from "react";
import api from "../services/api";
import { useAuth } from "./AuthContext";

const CartContext = createContext();

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState({ items: [], total: 0, item_count: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCart = useCallback(async () => {
    if (!user || user.role !== "customer") {
      setCart({ items: [], total: 0, item_count: 0 });
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/cart");
      setCart(res.data);
    } catch {
      setCart({ items: [], total: 0, item_count: 0 });
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  // Run a cart mutation; on success update state, on failure resync with the
  // server (so the UI never shows a stale/empty cart) and surface the error.
  const safeMutate = async (requestFn) => {
    setError(null);
    try {
      const res = await requestFn();
      setCart(res.data);
      return res.data;
    } catch (err) {
      fetchCart();
      const detail = err?.response?.data?.detail;
      setError(detail || "Failed to update cart.");
      throw err;
    }
  };

  const addToCart = (productId, quantity = 1) =>
    safeMutate(() => api.post("/cart/items", { product_id: productId, quantity }));
  const updateQuantity = (productId, quantity) =>
    safeMutate(() => api.put(`/cart/items/${productId}`, { quantity }));
  const removeFromCart = (productId) =>
    safeMutate(() => api.delete(`/cart/items/${productId}`));
  const clearCart = () => safeMutate(() => api.delete("/cart"));

  return (
    <CartContext.Provider
      value={{ cart, loading, error, addToCart, updateQuantity, removeFromCart, clearCart, fetchCart }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  return useContext(CartContext);
}
