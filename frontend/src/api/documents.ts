/**
 * API functions for fetching handbook documents.
 *
 * @module api/documents
 */

import { apiFetch } from "./client";
import type { DocumentDetail, DocumentSummary } from "@/types/documents";

/**
 * Fetch all handbook documents ordered by display position.
 *
 * @returns A list of document summaries.
 */
export function fetchDocuments(): Promise<DocumentSummary[]> {
  return apiFetch<DocumentSummary[]>("/api/docs");
}

/**
 * Fetch a single document with all its parsed sections.
 *
 * @param slug - URL-friendly document identifier.
 * @returns The full document with sections.
 */
export function fetchDocument(slug: string): Promise<DocumentDetail> {
  return apiFetch<DocumentDetail>(`/api/docs/${slug}`);
}
