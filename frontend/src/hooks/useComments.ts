/**
 * TanStack Query hooks for section comments.
 *
 * @module hooks/useComments
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createComment, fetchComments } from "@/api/comments";

/**
 * Fetch threaded comments for a section.
 *
 * @param slug - Document slug.
 * @param anchor - Section anchor.
 * @returns Query result with comment threads.
 */
export function useComments(slug: string, anchor: string) {
  return useQuery({
    queryKey: ["comments", slug, anchor],
    queryFn: () => fetchComments(slug, anchor),
    enabled: !!slug && !!anchor,
  });
}

/**
 * Mutation hook for creating a new comment.
 *
 * Automatically invalidates the comments query on success so
 * the UI updates without a manual refetch.
 *
 * @param slug - Document slug.
 * @param anchor - Section anchor.
 * @returns Mutation result with create function.
 */
export function useCreateComment(slug: string, anchor: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ body, parentId }: { body: string; parentId?: string }) =>
      createComment(slug, anchor, body, parentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["comments", slug, anchor] });
    },
  });
}
