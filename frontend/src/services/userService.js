import api from "./api";

// User service: real backend endpoints (replace with FastAPI/Mongo).
export const userService = {
  getMe: () => api.get("/users/me").then((r) => r.data),
  updateProfile: (data) => api.patch("/users/me", data).then((r) => r.data),
  changePassword: (data) =>
    api.patch("/users/me/password", data).then((r) => r.data),
};
