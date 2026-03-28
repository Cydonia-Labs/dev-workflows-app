/**
 * Notification inbox page with mark-read and push subscription controls.
 *
 * @module pages/NotificationsPage
 */

import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useNotifications, useMarkRead } from "@/hooks/useNotifications";
import { usePushSubscription } from "@/hooks/usePushSubscription";
import "./NotificationsPage.css";

/** Display the current user's notifications with inbox management. */
export function NotificationsPage() {
  const { isAuthenticated } = useAuth();
  const { data: notifications, isLoading } = useNotifications(isAuthenticated);
  const markRead = useMarkRead();
  const push = usePushSubscription(isAuthenticated);

  if (isLoading) return <p>Loading notifications...</p>;

  const unread = notifications?.filter((n) => !n.is_read) ?? [];

  function handleMarkAllRead() {
    if (!unread.length) return;
    markRead.mutate(unread.map((n) => n.id));
  }

  return (
    <div className="notifications-page">
      <div className="notifications-header">
        <h1>Notifications</h1>
        <div className="notifications-actions">
          {unread.length > 0 && (
            <button className="btn-text" onClick={handleMarkAllRead} disabled={markRead.isPending}>
              Mark all read ({unread.length})
            </button>
          )}
        </div>
      </div>

      <div className="push-settings">
        {push.supported ? (
          push.subscribed ? (
            <p className="push-status">Push notifications enabled.</p>
          ) : push.permission === "denied" ? (
            <p className="push-status push-denied">
              Push notifications were denied. Enable them in your browser settings.
            </p>
          ) : (
            <button className="btn-primary btn-small" onClick={push.subscribe}>
              Enable push notifications
            </button>
          )
        ) : (
          <p className="push-status">Push notifications are not supported in this browser.</p>
        )}
      </div>

      {notifications && notifications.length > 0 ? (
        <ul className="notification-list">
          {notifications.map((n) => (
            <li key={n.id} className={n.is_read ? "read" : "unread"}>
              {n.link ? (
                <Link to={n.link} className="notification-link">
                  <strong>{n.title}</strong>
                  <p>{n.body}</p>
                </Link>
              ) : (
                <div>
                  <strong>{n.title}</strong>
                  <p>{n.body}</p>
                </div>
              )}
              <small>{new Date(n.created_at).toLocaleString()}</small>
            </li>
          ))}
        </ul>
      ) : (
        <p className="no-notifications">No notifications yet.</p>
      )}
    </div>
  );
}
