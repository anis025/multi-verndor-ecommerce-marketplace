import api from "./api";

export const adminUsersService = {
  list: (params = {}) => api.get("/admin/users", { params }).then((r) => r.data),
  getById: (id) => api.get(`/admin/users/${id}`).then((r) => r.data),
  updateStatus: (id, isActive) =>
    api.patch(`/admin/users/${id}/status`, { is_active: isActive }).then((r) => r.data),
  resetPassword: (id, newPassword = null) =>
    api
      .post(`/admin/users/${id}/reset-password`, newPassword ? { new_password: newPassword } : {})
      .then((r) => r.data),
  changeRole: (id, role) =>
    api.post(`/admin/users/${id}/role`, { role }).then((r) => r.data),
  verifyEmail: (id) =>
    api.post(`/admin/users/${id}/verify-email`).then((r) => r.data),
};
