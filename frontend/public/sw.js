/**
 * Service worker for push notification display and click handling.
 *
 * Listens for push events from the Web Push API and displays
 * notifications. Handles notification clicks by navigating to
 * the deep link URL included in the push payload.
 */

/* eslint-disable no-restricted-globals */

self.addEventListener("push", (event) => {
  if (!event.data) return;

  let data;
  try {
    data = event.data.json();
  } catch {
    data = { title: "New notification", body: event.data.text() };
  }

  const options = {
    body: data.body || "",
    icon: "/icon-192.png",
    badge: "/icon-192.png",
    data: { link: data.link || "/" },
    tag: data.type || "default",
  };

  event.waitUntil(self.registration.showNotification(data.title || "Dev Workflows", options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  const link = event.notification.data?.link || "/";

  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      // Focus an existing window if one is open
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && "focus" in client) {
          client.navigate(link);
          return client.focus();
        }
      }
      // Otherwise open a new window
      return self.clients.openWindow(link);
    }),
  );
});
