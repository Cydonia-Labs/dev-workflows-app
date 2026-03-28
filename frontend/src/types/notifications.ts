/** A single notification for the user. */
export interface NotificationResponse {
  /** Notification unique identifier. */
  id: string;
  /** Event type (new_comment, pr_submitted, etc.). */
  type: string;
  /** Short notification title. */
  title: string;
  /** Notification body text. */
  body: string;
  /** Deep link into the app. */
  link: string | null;
  /** Whether the user has seen this notification. */
  is_read: boolean;
  /** When the notification was created. */
  created_at: string;
}
