/**
 * TanStack Query hooks for document data fetching.
 *
 * @module hooks/useDocuments
 */

import { useQuery } from "@tanstack/react-query";
import { fetchDocument, fetchDocuments } from "@/api/documents";

/**
 * Fetch all handbook documents.
 *
 * @returns Query result with a list of document summaries.
 */
export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: fetchDocuments,
  });
}

/**
 * Fetch a single document with sections.
 *
 * @param slug - URL-friendly document identifier.
 * @returns Query result with full document detail.
 */
export function useDocument(slug: string) {
  return useQuery({
    queryKey: ["documents", slug],
    queryFn: () => fetchDocument(slug),
    enabled: !!slug,
  });
}
