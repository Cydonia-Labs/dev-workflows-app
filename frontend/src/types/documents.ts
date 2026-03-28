/** Abbreviated document info for list views. */
export interface DocumentSummary {
  /** URL-friendly document identifier. */
  slug: string;
  /** Document title from H1 heading. */
  title: string;
  /** Display ordering position. */
  sort_order: number;
}

/** A parsed section within a document. */
export interface SectionResponse {
  /** Section unique identifier. */
  id: string;
  /** URL-safe anchor for deep linking. */
  anchor: string;
  /** Section heading text. */
  title: string;
  /** 2 for H2, 3 for H3. */
  heading_level: number;
  /** Markdown content of the section. */
  content: string;
  /** Position within the document. */
  sort_order: number;
  /** Number of comments on this section. */
  comment_count: number;
}

/** Full document with parsed sections. */
export interface DocumentDetail {
  /** URL-friendly document identifier. */
  slug: string;
  /** Document title from H1 heading. */
  title: string;
  /** Full markdown content. */
  raw_markdown: string;
  /** Parsed sections in display order. */
  sections: SectionResponse[];
  /** Git commit SHA at last sync. */
  github_sha: string;
  /** When the document was last synced. */
  synced_at: string;
}
