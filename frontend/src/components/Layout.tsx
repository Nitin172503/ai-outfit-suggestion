import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">Outfit AI</div>
        <nav>
          <NavLink to="/wardrobe">Wardrobe</NavLink>
          <NavLink to="/suggestions">Suggestions</NavLink>
          <NavLink to="/library">Library</NavLink>
          <NavLink to="/color-book">Color Book</NavLink>
        </nav>
        <div className="user-area">
          <span>{user?.full_name || user?.email}</span>
          <button onClick={handleLogout}>Log out</button>
        </div>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
