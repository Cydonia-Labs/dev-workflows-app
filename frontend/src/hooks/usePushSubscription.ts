/**
 * Hook for managing Web Push notification subscriptions.
 *
 * Handles requesting permission, subscribing via the Push API,
 * and registering the subscription with the backend.
 *
 * @module hooks/usePushSubscription
 */

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/api/client";

/** State of the push subscription. */
interface PushState {
  /** Whether the browser supports push notifications. */
  supported: boolean;
  /** Current notification permission ("default", "granted", "denied"). */
  permission: NotificationPermission | "unsupported";
  /** Whether the user is currently subscribed to push notifications. */
  subscribed: boolean;
  /** Subscribe to push notifications (requests permission if needed). */
  subscribe: () => Promise<void>;
}

/**
 * Manage the Web Push subscription lifecycle.
 *
 * On mount, checks if the browser supports push and whether
 * an active subscription exists. Provides a subscribe function
 * that requests permission and registers with the backend.
 *
 * @param isAuthenticated - Whether the user is logged in.
 * @returns The current push subscription state and subscribe function.
 */
export function usePushSubscription(isAuthenticated: boolean): PushState {
  const [supported] = useState(() => "serviceWorker" in navigator && "PushManager" in window);
  const [permission, setPermission] = useState<NotificationPermission | "unsupported">(
    supported ? Notification.permission : "unsupported",
  );
  const [subscribed, setSubscribed] = useState(false);

  // Check for existing subscription on mount
  useEffect(() => {
    if (!supported || !isAuthenticated) return;

    navigator.serviceWorker.ready
      .then((reg) => reg.pushManager.getSubscription())
      .then((sub) => setSubscribed(sub !== null))
      .catch(() => setSubscribed(false));
  }, [supported, isAuthenticated]);

  const subscribe = useCallback(async () => {
    if (!supported) return;

    // Request notification permission
    const perm = await Notification.requestPermission();
    setPermission(perm);
    if (perm !== "granted") return;

    // Get VAPID public key from backend
    const { public_key } = await apiFetch<{ public_key: string }>("/api/notifications/vapid-key");
    if (!public_key) return;

    // Subscribe via the Push API
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(public_key),
    });

    // Send subscription to backend
    const subJson = subscription.toJSON();
    await apiFetch("/api/notifications/subscribe", {
      method: "POST",
      body: JSON.stringify({
        endpoint: subscription.endpoint,
        keys: {
          p256dh: subJson.keys?.p256dh ?? "",
          auth: subJson.keys?.auth ?? "",
        },
      }),
    });

    setSubscribed(true);
  }, [supported]);

  return { supported, permission, subscribed, subscribe };
}

/**
 * Convert a base64-encoded VAPID key to a Uint8Array for the Push API.
 *
 * The Push API requires the applicationServerKey as a Uint8Array,
 * but VAPID keys are typically stored and transmitted as base64.
 *
 * @param base64String - The base64url-encoded VAPID public key.
 * @returns A Uint8Array suitable for pushManager.subscribe().
 */
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; i++) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}
