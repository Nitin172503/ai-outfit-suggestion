import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";
import BrandMark from "../components/BrandMark";

const DEMO_EMAIL = "demo@outfitai.app";
const DEMO_PASSWORD = "OutfitDemo123!";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [demoBusy, setDemoBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(email, password);
      navigate("/wardrobe");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  async function onViewDemo() {
    setError("");
    setDemoBusy(true);
    try {
      await login(DEMO_EMAIL, DEMO_PASSWORD);
      navigate("/wardrobe");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Demo account is unavailable right now");
    } finally {
      setDemoBusy(false);
    }
  }

  return (
    <div className="auth-page bg-wash">
      <form className="auth-card" onSubmit={onSubmit}>
        <Link to="/" className="brand-link">
          <BrandMark />
          Outfit AI
        </Link>
        <p className="subtitle">Log in to your wardrobe</p>
        {error && <div className="form-error">{error}</div>}
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <button type="submit" disabled={busy}>
          {busy ? "Logging in…" : "Log in"}
        </button>
        <button type="button" className="secondary" onClick={onViewDemo} disabled={demoBusy}>
          {demoBusy ? "Loading demo…" : "View demo instead"}
        </button>
        <p className="auth-switch">
          No account? <Link to="/register">Create one</Link>
        </p>
      </form>
    </div>
  );
}
