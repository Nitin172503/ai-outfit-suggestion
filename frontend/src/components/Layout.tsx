import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import BrandMark from "./BrandMark";

const NAV_ITEMS = [
  {
    to: "/wardrobe",
    label: "Wardrobe",
    icon: (
      <path d="M9 3.5 7 6c-1.2.3-2 1.3-2 2.5v9A1.5 1.5 0 0 0 6.5 19h11a1.5 1.5 0 0 0 1.5-1.5v-9c0-1.2-.8-2.2-2-2.5l-2-2.5M9 3.5a3 3 0 0 0 6 0" />
    ),
  },
  {
    to: "/suggestions",
    label: "Suggestions",
    icon: <path d="M12 3v2m6.4-.4-1.4 1.4M21 12h-2M7 12H5m1.4-6.4L5 4.2M12 8a4 4 0 0 1 4 4c0 1.7-1 2.6-1.7 3.3-.5.5-.8 1-.9 1.7H9.6c-.1-.7-.4-1.2-.9-1.7C7.9 14.6 8 13.7 8 12a4 4 0 0 1 4-4Zm-1.5 11h3" />,
  },
  {
    to: "/library",
    label: "Library",
    icon: <path d="M6 4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v16l-6-4-6 4V4Z" strokeLinecap="round" />,
  },
  {
    to: "/color-book",
    label: "Color Book",
    icon: <path d="M12 21a9 9 0 1 1 0-18c4 0 8 2.6 8 7.5 0 2-1.2 3.5-3.3 3.5H15c-.7 0-1.2.6-1.2 1.2 0 .3.1.5.3.8.5.6.9 1.1.9 1.9 0 1.7-1.4 3.1-3 3.1Zm-4.5-9.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm2-4a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm5 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm2 4a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" />,
  },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const initial = (user?.full_name || user?.email || "?").trim().charAt(0).toUpperCase();

  return (
    <div className="app-shell">
      <header className="topbar">
        <NavLink to="/wardrobe" className="brand">
          <BrandMark size={26} />
          Outfit AI
        </NavLink>
        <nav>
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to}>
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round">
                {item.icon}
              </svg>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="user-area">
          <span className="user-avatar">{initial}</span>
          <span>{user?.full_name || user?.email}</span>
          <button className="secondary" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
