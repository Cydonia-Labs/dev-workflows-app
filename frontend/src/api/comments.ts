/**
 * API functions for section comments.
 *
 * @module api/comments
 */

import { apiFetch } from "./client";
import type { CommentResponse, CommentThread } from "@/types/comments";

/**
 * Fetch threaded comments for a document section.
 *
 * @param slug - Document slug.
 * @param anchor - Section anchor.
 * @returns Top-level comments with nested replies.
 */
export function fetchComments(slug: string, anchor: string): Promise<CommentThread[]> {
  return apiFetch<CommentThread[]>(`/api/docs/${slug}/sections/${anchor}/comments`);
}

/**
 * Create a new comment or reply on a section.
 *
 * @param slug - Document slug.
 * @param anchor - Section anchor.
 * @param body - Comment text in markdown.
 * @param parentId - Parent comment ID for replies, or undefined for top-level.
 * @returns The created comment.
 */
export function createComment(
  slug: string,
  anchor: string,
  body: string,
  parentId?: string,
): Promise<CommentResponse> {
  return apiFetch<CommentResponse>(`/api/docs/${slug}/sections/${anchor}/comments`, {
    method: "POST",
    body: JSON.stringify({ body, parent_id: parentId ?? null }),
  });
}
