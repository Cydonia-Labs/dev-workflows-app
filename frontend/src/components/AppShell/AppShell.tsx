/**
 * Application shell layout with sidebar navigation and top bar.
 *
 * Desktop: fixed sidebar on the left, top bar, content area.
 * Mobile: sidebar hidden, replaced by a hamburger menu dropdown
 * in the top bar.
 *
 * @module components/AppShell
 */

import { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useDocuments } from "@/hooks/useDocuments";
import { NotificationBell } from "@/components/NotificationBell";
import "./AppShell.css";

/** Top-level layout component wrapping all routes. */
export function AppShell() {
  const { user, isAuthenticated, login, logout } = useAuth();
  const { data: documents } = useDocuments();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  /** Close the mobile menu when a link is clicked. */
  function handleNavClick() {
    setMobileMenuOpen(false);
  }

  /** Shared navigation content used by both sidebar and mobile menu. */
  const navContent = (
    <>
      <h3 className="sidebar-heading">Handbook</h3>
      <ul>
        {documents?.map((doc) => (
          <li key={doc.slug}>
            <Link
              to={`/docs/${doc.slug}`}
              className={location.pathname === `/docs/${doc.slug}` ? "active" : ""}
              onClick={handleNavClick}
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
              <Link
                to="/changes"
                className={location.pathname === "/changes" ? "active" : ""}
                onClick={handleNavClick}
              >
                Open Changes
              </Link>
            </li>
            <li>
              <Link
                to="/notifications"
                className={location.pathname === "/notifications" ? "active" : ""}
                onClick={handleNavClick}
              >
                Notifications
              </Link>
            </li>
          </ul>
        </>
      )}
    </>
  );

  return (
    <div className="app-shell">
      {/* Desktop sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand-row">
          <a href="https://cydonialabs.com">
            <img src="/logo.png" alt="Cydonia Labs" className="sidebar-logo" />
          </a>
          <Link to="/" className="sidebar-brand">
            Dev Workflows
          </Link>
        </div>
        <nav className="sidebar-nav">{navContent}</nav>
      </aside>

      <div className="main-area">
        <header className="top-bar">
          <div className="top-bar-left">
            {/* Hamburger — visible only on mobile */}
            <button
              className="hamburger"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle navigation menu"
            >
              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                {mobileMenuOpen ? (
                  <>
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </>
                ) : (
                  <>
                    <line x1="3" y1="6" x2="21" y2="6" />
                    <line x1="3" y1="12" x2="21" y2="12" />
                    <line x1="3" y1="18" x2="21" y2="18" />
                  </>
                )}
              </svg>
            </button>
            {/* Brand — visible only on mobile */}
            <Link to="/" className="mobile-brand" onClick={handleNavClick}>
              Dev Workflows
            </Link>
          </div>
          <div className="top-bar-right">
            <NotificationBell />
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

        {/* Mobile dropdown menu */}
        {mobileMenuOpen && <nav className="mobile-menu">{navContent}</nav>}

        <main className="content">
          <Outlet />
        </main>

        <footer className="app-footer">
          <span>&copy; {new Date().getFullYear()} Cydonia Labs. All rights reserved.</span>
          <span className="footer-sep">|</span>
          <a href="https://github.com/Cydonia-Labs/dev-workflows-app/blob/main/LICENSE">
            MIT License
          </a>
        </footer>
      </div>
    </div>
  );
}
