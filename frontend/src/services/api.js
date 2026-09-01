import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const verifyEmail = (email, otp) => api.post("/auth/verify-email", { email, otp });
export const resendOtp = (email) => api.post("/auth/resend-otp", { email });

export const adminResetPassword = (userId, newPassword) =>
  api.post(`/admin/users/${userId}/reset-password`, { new_password: newPassword });
export const adminChangeRole = (userId, role) =>
  api.post(`/admin/users/${userId}/role`, { role });

// Multipart upload of a product image (from the seller's computer).
// Returns { image_url, filename }.
export const uploadProductImage = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api
    .post("/sellers/me/products/upload-image", form, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
};

export default api;
