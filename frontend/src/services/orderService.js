import api from "./api";

export const orderService = {
  list: (params = {}) =>
    api.get("/orders", { params }).then((r) => r.data),
  getById: (id) => api.get(`/orders/${id}`).then((r) => r.data),
  cancel: (id) => api.patch(`/orders/${id}/cancel`).then((r) => r.data),
};
