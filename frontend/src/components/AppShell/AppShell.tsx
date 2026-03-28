/**
 * Application shell layout with sidebar navigation and top bar.
 *
 * Provides the persistent layout structure — sidebar with doc nav
 * on the left, top bar with user menu, and main content area.
 *
 * @module components/AppShell
 */

import { Outlet, Link, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useDocuments } from "@/hooks/useDocuments";
import "./AppShell.css";

/** Top-level layout component wrapping all routes. */
export function AppShell() {
  const { user, isAuthenticated, login, logout } = useAuth();
  const { data: documents } = useDocuments();
  const location = useLocation();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link to="/" className="sidebar-brand">
          Dev Workflows
        </Link>

        <nav className="sidebar-nav">
          <h3 className="sidebar-heading">Handbook</h3>
          <ul>
            {documents?.map((doc) => (
              <li key={doc.slug}>
                <Link
                  to={`/docs/${doc.slug}`}
                  className={location.pathname === `/docs/${doc.slug}` ? "active" : ""}
                >
                  {doc.title}
                </Link>
              </li>
            ))}
          </ul>

          {isAuthenticated && (
            <>
              <h3 className="sidebar-heading">Collaborate</h3>
              <ul>
                <li>
                  <Link to="/changes" className={location.pathname === "/changes" ? "active" : ""}>
                    Open Changes
                  </Link>
                </li>
                <li>
                  <Link
                    to="/notifications"
                    className={location.pathname === "/notifications" ? "active" : ""}
                  >
                    Notifications
                  </Link>
                </li>
              </ul>
            </>
          )}
        </nav>
      </aside>

      <div className="main-area">
        <header className="top-bar">
          <div className="top-bar-left" />
          <div className="top-bar-right">
            {isAuthenticated ? (
              <div className="user-menu">
                {user?.avatar_url && <img src={user.avatar_url} alt="" className="avatar" />}
                <span className="username">{user?.display_name}</span>
                <button onClick={logout} className="btn-text">
                  Log out
                </button>
              </div>
            ) : (
              <button onClick={login} className="btn-primary">
                Sign in with GitHub
              </button>
            )}
          </div>
        </header>

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
