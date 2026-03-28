import type { UserResponse } from "./auth";

/** A single comment with author info. */
export interface CommentResponse {
  /** Comment unique identifier. */
  id: string;
  /** The user who wrote the comment. */
  author: UserResponse;
  /** Comment text in markdown. */
  body: string;
  /** Parent comment ID if this is a reply. */
  parent_id: string | null;
  /** Whether this thread is marked as resolved. */
  is_resolved: boolean;
  /** When the comment was posted. */
  created_at: string;
  /** When the comment was last edited. */
  updated_at: string;
}

/** A top-level comment with its nested replies. */
export interface CommentThread extends CommentResponse {
  /** Child comments in chronological order. */
  replies: CommentResponse[];
}
