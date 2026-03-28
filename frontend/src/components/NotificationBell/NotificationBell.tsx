/**
 * Notification bell icon with unread count badge.
 *
 * Displayed in the top bar. Shows the number of unread notifications
 * and links to the notifications page.
 *
 * @module components/NotificationBell
 */

import { Link } from "react-router-dom";
import { useUnreadCount } from "@/hooks/useNotifications";
import { useAuth } from "@/contexts/AuthContext";
import "./NotificationBell.css";

/** Notification bell with unread badge, shown for authenticated users. */
export function NotificationBell() {
  const { isAuthenticated } = useAuth();
  const unreadCount = useUnreadCount(isAuthenticated);

  if (!isAuthenticated) return null;

  return (
    <Link to="/notifications" className="notification-bell" title="Notifications">
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
      </svg>
      {unreadCount > 0 && <span className="bell-badge">{unreadCount}</span>}
    </Link>
  );
}
