/**
 * API functions for notifications.
 *
 * @module api/notifications
 */

import { apiFetch } from "./client";
import type { NotificationResponse } from "@/types/notifications";

/**
 * Fetch the current user's notifications, newest first.
 *
 * @param limit - Maximum number to return.
 * @param offset - Number to skip for pagination.
 * @returns A list of notifications.
 */
export function fetchNotifications(limit = 50, offset = 0): Promise<NotificationResponse[]> {
  return apiFetch<NotificationResponse[]>(`/api/notifications?limit=${limit}&offset=${offset}`);
}

/**
 * Mark specified notifications as read.
 *
 * @param notificationIds - IDs of notifications to mark read.
 * @returns The number of notifications updated.
 */
export function markNotificationsRead(notificationIds: string[]): Promise<{ updated: number }> {
  return apiFetch<{ updated: number }>("/api/notifications/read", {
    method: "POST",
    body: JSON.stringify({ notification_ids: notificationIds }),
  });
}
