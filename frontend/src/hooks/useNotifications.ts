/**
 * TanStack Query hooks for notifications.
 *
 * @module hooks/useNotifications
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchNotifications, markNotificationsRead } from "@/api/notifications";

/**
 * Fetch the current user's notifications.
 *
 * Polls every 60 seconds to keep the badge count up to date.
 * Only enabled when the user is authenticated.
 *
 * @param enabled - Whether to enable the query (pass isAuthenticated).
 * @returns Query result with a list of notifications.
 */
export function useNotifications(enabled: boolean) {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: () => fetchNotifications(),
    enabled,
    refetchInterval: 60_000,
  });
}

/**
 * Get the unread notification count.
 *
 * @param enabled - Whether to enable the query.
 * @returns The number of unread notifications, or 0 if loading/disabled.
 */
export function useUnreadCount(enabled: boolean): number {
  const { data } = useNotifications(enabled);
  if (!data) return 0;
  return data.filter((n) => !n.is_read).length;
}

/**
 * Mutation hook for marking notifications as read.
 *
 * Invalidates the notifications query on success so the
 * unread count updates.
 *
 * @returns Mutation result with the mark-read function.
 */
export function useMarkRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (ids: string[]) => markNotificationsRead(ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}
