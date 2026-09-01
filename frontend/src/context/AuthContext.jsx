import { createContext, useContext, useState, useEffect } from "react";
import api, { verifyEmail as verifyEmailRequest, resendOtp as resendOtpRequest } from "../services/api";
import { adminAuthService } from "../services/adminAuthService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      api.get("/auth/me")
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem("token");
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    localStorage.setItem("token", res.data.access_token);
    setUser(res.data.user);
    return res.data;
  };

  const register = async (data) => {
    const res = await api.post("/auth/register", data);
    // No token yet: the account must be verified via the OTP flow.
    return res.data;
  };

  const verifyEmail = async (email, otp) => {
    const res = await verifyEmailRequest(email, otp);
    localStorage.setItem("token", res.data.access_token);
    setUser(res.data.user);
    return res.data;
  };

  const resendOtp = async (email) => {
    const res = await resendOtpRequest(email);
    return res.data;
  };

  // Dedicated admin authentication — passwordless email OTP, restricted
  // server-side to a single configured email address.
  const requestAdminOtp = async (email) => {
    return adminAuthService.requestOtp(email);
  };

  const verifyAdminOtp = async (email, otp) => {
    const data = await adminAuthService.verifyOtp(email, otp);
    window.history.replaceState(null, "", "/admin");
    localStorage.setItem("token", data.access_token);
    setUser({
      id: data.user_id,
      email: data.email,
      name: data.name,
      role: "admin",
    });
    return data;
  };

  const adminLogout = async () => {
    try {
      await adminAuthService.logout();
    } catch {
      // ignore
    }
    window.history.replaceState(null, "", "/admin/login");
    localStorage.removeItem("token");
    setUser(null);
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      // ignore
    }
    // Replace the current history entry so the browser back button cannot
    // return to a protected dashboard page after the user has logged out.
    window.history.replaceState(null, "", "/login");
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, register, verifyEmail, resendOtp, logout, requestAdminOtp, verifyAdminOtp, adminLogout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
