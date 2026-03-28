/**
 * Page for viewing a single handbook document with section navigation.
 *
 * Renders the full markdown document with a table of contents sidebar
 * built from the parsed sections. Each section has an anchor for deep
 * linking and shows a comment count badge.
 *
 * @module pages/DocViewPage
 */

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

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Document not found.</p>;
  if (!doc) return null;

  return (
    <div className="doc-view">
      <div className="doc-header">
        <h1>{doc.title}</h1>
        <div className="doc-meta">
          Last synced: {new Date(doc.synced_at).toLocaleDateString()}
          {isAuthenticated && (
            <Link to={`/changes/new?doc=${doc.slug}`} className="btn-primary">
              Propose Edit
            </Link>
          )}
        </div>
      </div>

      <div className="doc-layout">
        <nav className="table-of-contents">
          <h3>Contents</h3>
          <ul>
            {doc.sections.map((section) => (
              <li key={section.anchor} className={section.heading_level === 3 ? "toc-indent" : ""}>
                <a href={`#${section.anchor}`}>
                  {section.title}
                  {section.comment_count > 0 && (
                    <span className="comment-badge">{section.comment_count}</span>
                  )}
                </a>
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
              {section.heading_level === 2 && (
                <SectionComments
                  slug={doc.slug}
                  anchor={section.anchor}
                  commentCount={section.comment_count}
                />
              )}
            </div>
          ))}
        </article>
      </div>
    </div>
  );
}
