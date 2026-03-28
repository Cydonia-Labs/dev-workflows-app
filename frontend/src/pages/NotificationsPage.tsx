/**
 * Notification inbox page.
 *
 * @module pages/NotificationsPage
 */

import { useQuery } from "@tanstack/react-query";
import { fetchNotifications } from "@/api/notifications";

/** Display the current user's notifications. */
export function NotificationsPage() {
  const { data: notifications, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => fetchNotifications(),
  });

  if (isLoading) return <p>Loading notifications...</p>;

  return (
    <div>
      <h1>Notifications</h1>
      {notifications && notifications.length > 0 ? (
        <ul className="notification-list">
          {notifications.map((n) => (
            <li key={n.id} className={n.is_read ? "read" : "unread"}>
              <strong>{n.title}</strong>
              <p>{n.body}</p>
              <small>{new Date(n.created_at).toLocaleString()}</small>
            </li>
          ))}
        </ul>
      ) : (
        <p>No notifications yet.</p>
      )}
    </div>
  );
}
