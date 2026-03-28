/**
 * Page for viewing a single handbook document with section navigation.
 *
 * Renders the full markdown document with a table of contents sidebar
 * built from the parsed sections. Each section has an anchor for deep
 * linking and shows a comment count badge in the ToC.
 *
 * Discussion is accessed via a top-level button that opens a panel
 * with a section picker — keeps the document content clean.
 *
 * @module pages/DocViewPage
 */

import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useDocument } from "@/hooks/useDocuments";
import { useAuth } from "@/contexts/AuthContext";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { SectionComments } from "@/components/SectionComments";
import "./DocViewPage.css";

/** View a single handbook document with table of contents. */
export function DocViewPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: doc, isLoading, error } = useDocument(slug ?? "");
  const { isAuthenticated } = useAuth();
  const [discussionAnchor, setDiscussionAnchor] = useState<string | null>(null);

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Document not found.</p>;
  if (!doc) return null;

  const totalComments = doc.sections.reduce((sum, s) => sum + s.comment_count, 0);
  const h2Sections = doc.sections.filter((s) => s.heading_level === 2);

  /**
   * Find the H2 anchor that owns a given section.
   * For H2 sections, returns itself. For H3, returns its parent H2.
   */
  function getDiscussionAnchor(sectionAnchor: string): string | null {
    const sections = doc?.sections ?? [];
    let lastH2: string | null = null;
    for (const s of sections) {
      if (s.heading_level === 2) lastH2 = s.anchor;
      if (s.anchor === sectionAnchor) return lastH2;
    }
    return null;
  }

  /** Open the discussion panel directly to a section's H2 discussion. */
  function openDiscussionFor(sectionAnchor: string) {
    const h2Anchor = getDiscussionAnchor(sectionAnchor);
    if (h2Anchor) setDiscussionAnchor(h2Anchor);
  }

  return (
    <div className="doc-view">
      <div className="doc-header">
        <h1>{doc.title}</h1>
        <div className="doc-meta">
          <span>Last synced: {new Date(doc.synced_at).toLocaleDateString()}</span>
          <div className="doc-actions">
            <button
              className="btn-secondary"
              onClick={() =>
                setDiscussionAnchor(discussionAnchor ? null : (h2Sections[0]?.anchor ?? null))
              }
            >
              Discussion{totalComments > 0 ? ` (${totalComments})` : ""}
            </button>
            {isAuthenticated && (
              <Link to={`/changes/new?doc=${doc.slug}`} className="btn-primary">
                Propose Edit
              </Link>
            )}
          </div>
        </div>
      </div>

      {discussionAnchor && (
        <div className="discussion-panel">
          <div className="discussion-header">
            <h3>Discussion</h3>
            <select
              className="section-picker"
              value={discussionAnchor}
              onChange={(e) => setDiscussionAnchor(e.target.value)}
            >
              {h2Sections.map((s) => (
                <option key={s.anchor} value={s.anchor}>
                  {s.title}
                  {s.comment_count > 0 ? ` (${s.comment_count})` : ""}
                </option>
              ))}
            </select>
            <button className="btn-text" onClick={() => setDiscussionAnchor(null)}>
              Close
            </button>
          </div>
          <SectionComments
            slug={doc.slug}
            anchor={discussionAnchor}
            commentCount={
              doc.sections.find((s) => s.anchor === discussionAnchor)?.comment_count ?? 0
            }
          />
        </div>
      )}

      <div className="doc-layout">
        <nav className="table-of-contents">
          <h3>Contents</h3>
          <ul>
            {doc.sections.map((section) => (
              <li key={section.anchor} className={section.heading_level === 3 ? "toc-indent" : ""}>
                <a href={`#${section.anchor}`}>{section.title}</a>
                {section.comment_count > 0 && (
                  <button
                    className="comment-badge comment-badge-btn"
                    onClick={() => openDiscussionFor(section.anchor)}
                    title={`${section.comment_count} comment${section.comment_count > 1 ? "s" : ""} — click to open discussion`}
                  >
                    {section.comment_count}
                  </button>
                )}
              </li>
            ))}
          </ul>
        </nav>

        <article className="doc-content">
          {doc.sections.map((section) => (
            <div key={section.anchor} id={section.anchor} className="doc-section">
              <MarkdownRenderer
                content={`${"#".repeat(section.heading_level)} ${section.title}\n\n${section.content}`}
              />
            </div>
          ))}
        </article>
      </div>
    </div>
  );
}
