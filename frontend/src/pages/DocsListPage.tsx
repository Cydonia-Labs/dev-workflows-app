/**
 * Page listing all handbook documents.
 *
 * @module pages/DocsListPage
 */

import { Link } from "react-router-dom";
import { useDocuments } from "@/hooks/useDocuments";

/** Browse all handbook documents. */
export function DocsListPage() {
  const { data: documents, isLoading, error } = useDocuments();

  if (isLoading) return <p>Loading documents...</p>;
  if (error) return <p>Failed to load documents: {error.message}</p>;

  return (
    <div>
      <h1>Handbook</h1>
      {documents && documents.length > 0 ? (
        <div className="docs-grid">
          {documents.map((doc) => (
            <Link to={`/docs/${doc.slug}`} key={doc.slug} className="doc-card">
              <h3>{doc.title}</h3>
            </Link>
          ))}
        </div>
      ) : (
        <p>No documents available. Sync the handbook repo to get started.</p>
      )}
    </div>
  );
}
