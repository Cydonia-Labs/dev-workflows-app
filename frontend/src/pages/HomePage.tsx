/**
 * Landing page with an overview and links to browse the handbook.
 *
 * @module pages/HomePage
 */

import { Link } from "react-router-dom";
import { useDocuments } from "@/hooks/useDocuments";

/** The app's root landing page. */
export function HomePage() {
  const { data: documents, isLoading } = useDocuments();

  return (
    <div>
      <h1>Dev Workflows Handbook</h1>
      <p>
        A practical engineering handbook for solo founders scaling to teams. Browse the docs,
        discuss specific sections, and propose changes — all in one place.
      </p>

      <h2>Documents</h2>
      {isLoading ? (
        <p>Loading...</p>
      ) : documents && documents.length > 0 ? (
        <ul>
          {documents.map((doc) => (
            <li key={doc.slug}>
              <Link to={`/docs/${doc.slug}`}>{doc.title}</Link>
            </li>
          ))}
        </ul>
      ) : (
        <p>
          No documents synced yet. Push to the handbook repo or trigger a manual sync to get
          started.
        </p>
      )}
    </div>
  );
}
