import api from "./api";

// Passwordless admin login: request a one-time code, then verify it.
export const adminAuthService = {
  requestOtp: (email) =>
    api.post("/admin/auth/login", { email }).then((r) => r.data),
  verifyOtp: (email, otp) =>
    api.post("/admin/auth/verify-otp", { email, otp }).then((r) => r.data),
  logout: () => api.post("/admin/auth/logout").then((r) => r.data),
};
