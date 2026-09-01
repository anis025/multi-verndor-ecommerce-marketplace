import api from "./api";

export const cartService = {
  get: () => api.get("/cart").then((r) => r.data),
  addItem: (productId, quantity) =>
    api.post("/cart/items", { product_id: productId, quantity }).then((r) => r.data),
  updateItem: (productId, quantity) =>
    api.put(`/cart/items/${productId}`, { quantity }).then((r) => r.data),
  removeItem: (productId) =>
    api.delete(`/cart/items/${productId}`).then((r) => r.data),
  clear: () => api.delete("/cart").then((r) => r.data),
};
