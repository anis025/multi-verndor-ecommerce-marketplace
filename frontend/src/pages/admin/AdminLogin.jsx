import { useEffect, useRef, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function AdminLogin() {
  const navigate = useNavigate();
  const { requestAdminOtp, verifyAdminOtp } = useAuth();

  const [email, setEmail] = useState("mdanis.dev@gmail.com");
  const [step, setStep] = useState("email"); // "email" | "code"
  const [otp, setOtp] = useState("");
  const [error, setError] = useState(null);
  const [info, setInfo] = useState(null);
  const [busy, setBusy] = useState(false);
  const [resendIn, setResendIn] = useState(0);
  const cooldownRef = useRef(null);

  useEffect(() => () => clearInterval(cooldownRef.current), []);

  const startResendCooldown = (seconds = 60) => {
    setResendIn(seconds);
    clearInterval(cooldownRef.current);
    cooldownRef.current = setInterval(() => {
      setResendIn((c) => {
        if (c <= 1) {
          clearInterval(cooldownRef.current);
          return 0;
        }
        return c - 1;
      });
    }, 1000);
  };

  const sendCode = async (e) => {
    e?.preventDefault?.();
    setError(null);
    setInfo(null);
    setBusy(true);
    try {
      await requestAdminOtp(email);
      setStep("code");
      setInfo("A 6-digit sign-in code has been sent to your email.");
      startResendCooldown(60);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Could not send the sign-in code. Please try again."
      );
    } finally {
      setBusy(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError(null);
    if (!/^\d{6}$/.test(otp)) {
      setError("Enter the 6-digit code from your email.");
      return;
    }
    setBusy(true);
    try {
      await verifyAdminOtp(email, otp);
      navigate("/admin", { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail || "Verification failed.";
      setError(detail);
      setOtp("");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page admin-login-page">
      <div className="admin-login-container">
        <div className="admin-login-header">
          <div className="admin-login-mark">H</div>
          <h1>Admin Console</h1>
          <p className="dash-muted">Authorized personnel only.</p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {info && <div className="alert alert-success">{info}</div>}

        {step === "email" && (
          <form onSubmit={sendCode} className="admin-login-form" noValidate>
            <div className="form-group">
              <label>Admin email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="username"
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={busy}
            >
              {busy ? "Sending…" : "Send sign-in code"}
            </button>
          </form>
        )}

        {step === "code" && (
          <form onSubmit={handleVerify} className="admin-login-form" noValidate>
            <div className="form-group">
              <label>Email</label>
              <input type="email" value={email} disabled />
            </div>
            <div className="form-group">
              <label>6-digit code</label>
              <input
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={6}
                value={otp}
                onChange={(e) =>
                  setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
                }
                className="otp-input"
                placeholder="123456"
                autoFocus
                required
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={busy || otp.length !== 6}
            >
              {busy ? "Verifying…" : "Sign in"}
            </button>
            <div className="admin-login-foot" style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
              <button
                type="button"
                className="btn-link"
                onClick={() => { setStep("email"); setOtp(""); setError(null); setInfo(null); clearInterval(cooldownRef.current); setResendIn(0); }}
              >
                Use a different email
              </button>
              <button
                type="button"
                className="btn-link"
                onClick={sendCode}
                disabled={busy || resendIn > 0}
              >
                {resendIn > 0 ? `Resend in ${resendIn}s` : "Resend code"}
              </button>
            </div>
          </form>
        )}

        <p className="admin-login-foot">
          Not an admin? <Link to="/login">Customer login</Link>
        </p>
      </div>
    </div>
  );
}
