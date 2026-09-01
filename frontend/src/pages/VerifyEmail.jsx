import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const RESEND_COOLDOWN = 60;

export default function VerifyEmail() {
  const location = useLocation();
  const navigate = useNavigate();
  const { verifyEmail, resendOtp } = useAuth();

  const [email, setEmail] = useState(location.state?.email || "");
  const [emailStatus, setEmailStatus] = useState(location.state?.emailStatus || null);
  const [otp, setOtp] = useState("");
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(0);
  const timer = useRef(null);

  useEffect(() => {
    return () => clearInterval(timer.current);
  }, []);

  const startCooldown = () => {
    setCooldown(RESEND_COOLDOWN);
    clearInterval(timer.current);
    timer.current = setInterval(() => {
      setCooldown((c) => {
        if (c <= 1) {
          clearInterval(timer.current);
          return 0;
        }
        return c - 1;
      });
    }, 1000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);

    if (!/^\d{6}$/.test(otp)) {
      setError("Please enter the 6-digit code.");
      return;
    }

    setLoading(true);
    try {
      const data = await verifyEmail(email, otp);
      const role = data.user.role;
      if (role === "admin") navigate("/admin");
      else if (role === "seller") navigate("/seller");
      else navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Verification failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (cooldown > 0) return;
    setError(null);
    setMessage(null);
    try {
      await resendOtp(email);
      setMessage("A new code has been sent to your email.");
      startCooldown();
    } catch (err) {
      const detail = err.response?.data?.detail || "";
      setError(detail || "Could not resend code. Please try again.");
      if (/wait|Too many/i.test(detail)) startCooldown();
    }
  };

  return (
    <div className="page">
      <div className="auth-container">
        <h2>Verify your email</h2>
        <p className="role-hint">
          We sent a 6-digit verification code to <strong>{email}</strong>.
          Enter it below to activate your account.
        </p>

        {error && <div className="alert alert-error">{error}</div>}
        {message && <div className="alert alert-success">{message}</div>}
        {emailStatus && emailStatus !== "sent" && (
          <div className="alert alert-warning">
            We couldn't send the verification email (server email/SMTP not
            configured or failed). If you don't receive the code, ask the
            administrator to check the backend SMTP settings, then use "Resend code".
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="your@email.com"
            />
          </div>
          <div className="form-group">
            <label>Verification code</label>
            <input
              type="text"
              inputMode="numeric"
              maxLength={6}
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
              required
              placeholder="123456"
              className="otp-input"
            />
          </div>
          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? "Verifying..." : "Verify email"}
          </button>
        </form>

        <p className="auth-link">
          Didn't get the code?{" "}
          <button
            type="button"
            className="btn-link"
            onClick={handleResend}
            disabled={cooldown > 0}
          >
            {cooldown > 0 ? `Resend in ${cooldown}s` : "Resend code"}
          </button>
        </p>
        <p className="auth-link">
          <Link to="/login">Back to login</Link>
        </p>
      </div>
    </div>
  );
}
