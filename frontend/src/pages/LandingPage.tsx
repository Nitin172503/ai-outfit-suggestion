import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";
import BrandMark from "../components/BrandMark";

const DEMO_EMAIL = "demo@outfitai.app";
const DEMO_PASSWORD = "OutfitDemo123!";

export default function LandingPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [demoBusy, setDemoBusy] = useState(false);
  const [demoError, setDemoError] = useState("");

  if (user) return <Navigate to="/wardrobe" replace />;

  async function viewDemo() {
    setDemoBusy(true);
    setDemoError("");
    try {
      await login(DEMO_EMAIL, DEMO_PASSWORD);
      navigate("/wardrobe");
    } catch (err) {
      setDemoError(err instanceof ApiError ? err.message : "Demo account is unavailable right now");
    } finally {
      setDemoBusy(false);
    }
  }

  return (
    <div className="landing bg-wash">
      <header className="landing-nav">
        <Link to="/" className="brand-link">
          <BrandMark />
          Outfit AI
        </Link>
        <div className="landing-nav-actions">
          <Link to="/login" className="text-link">
            Log in
          </Link>
          <Link to="/register">
            <button>Get started</button>
          </Link>
        </div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <span className="hero-eyebrow">Local · No external AI</span>
          <h1>Know what to wear, from what you already own.</h1>
          <p>
            Photograph your wardrobe once. Outfit AI extracts each item's color straight from the
            photo, pairs pieces that work together, and scores every combination against a
            color-wheel engine — monochromatic, analogous, complementary, split-complementary,
            triadic. Save the outfits you like into libraries you can browse anytime.
          </p>
          <div className="hero-actions">
            <button onClick={viewDemo} disabled={demoBusy}>
              {demoBusy ? "Loading demo…" : "View demo"}
            </button>
            <Link to="/register" className="text-link">
              Create your own wardrobe →
            </Link>
          </div>
          {demoError && <div className="form-error">{demoError}</div>}
          <p className="hero-footnote">
            Demo signs you into a sample account with a 13-item wardrobe already loaded — no
            upload required.
          </p>
        </div>
        <div className="hero-art" aria-hidden="true">
          <HeroSwatchGrid />
        </div>
      </section>

      <section className="feature-grid">
        <div className="feature">
          <span className="feature-icon">
            <Icon path="M9 3.5 7 6c-1.2.3-2 1.3-2 2.5v9A1.5 1.5 0 0 0 6.5 19h11a1.5 1.5 0 0 0 1.5-1.5v-9c0-1.2-.8-2.2-2-2.5l-2-2.5M9 3.5a3 3 0 0 0 6 0" />
          </span>
          <h3>Upload once</h3>
          <p>Add a single photo, or a .zip of your whole closet at once. Colors are detected automatically from the pixels — no external service involved.</p>
        </div>
        <div className="feature">
          <span className="feature-icon">
            <Icon path="M12 3v2m6.4-.4-1.4 1.4M21 12h-2M7 12H5m1.4-6.4L5 4.2M12 8a4 4 0 0 1 4 4c0 1.7-1 2.6-1.7 3.3-.5.5-.8 1-.9 1.7H9.6c-.1-.7-.4-1.2-.9-1.7C7.9 14.6 8 13.7 8 12a4 4 0 0 1 4-4Zm-1.5 11h3" />
          </span>
          <h3>Get scored suggestions</h3>
          <p>Every outfit combination is ranked by how well its colors work together, using the same color-wheel rules a stylist would reach for.</p>
        </div>
        <div className="feature">
          <span className="feature-icon">
            <Icon path="M6 4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v16l-6-4-6 4V4Z" strokeLinecap="round" />
          </span>
          <h3>Build your library</h3>
          <p>Save outfits into named collections — work capsule, weekend rotation, travel packing — and come back to them anytime.</p>
        </div>
      </section>

      <footer className="landing-footer">
        <span>Outfit AI — runs entirely on local computation, no external AI service or dataset.</span>
      </footer>
    </div>
  );
}

function Icon({ path, strokeLinecap }: { path: string; strokeLinecap?: "round" }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" strokeLinecap={strokeLinecap}>
      <path d={path} />
    </svg>
  );
}

function HeroSwatchGrid() {
  const swatches = [
    "#16233F", "#C19A6B", "#F2EFE9", "#6E1F2A", "#2F4F3A", "#3B5B77",
    "#B5602C", "#8A9B6E", "#141414", "#B08D57", "#3A3A3A", "#F0F0EC",
  ];
  return (
    <div className="swatch-grid">
      {swatches.map((hex) => (
        <div key={hex} className="swatch-tile" style={{ background: hex }} />
      ))}
    </div>
  );
}
