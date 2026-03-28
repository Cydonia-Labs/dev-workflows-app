/**
 * Landing page with Cydonia Labs principles and handbook overview.
 *
 * @module pages/HomePage
 */

import { Link } from "react-router-dom";
import { useDocuments } from "@/hooks/useDocuments";
import "./HomePage.css";

/** The app's root landing page. */
export function HomePage() {
  const { data: documents, isLoading } = useDocuments();

  return (
    <div className="home-page">
      <section className="hero">
        <h1>Dev Workflows Handbook</h1>
        <p className="hero-sub">
          Built by{" "}
          <a href="https://cydonialabs.com" target="_blank" rel="noopener noreferrer">
            Cydonia Labs
          </a>{" "}
          — a practical engineering handbook for solo founders scaling to teams.
        </p>
      </section>

      <section className="principles">
        <h2>Our Principles</h2>
        <div className="principles-grid">
          <div className="principle">
            <h3>Ground Truth</h3>
            <p>
              Every claim is evidence-backed. Every decision is grounded in reality, not
              assumptions. We measure, we verify, and we build on what we can prove.
            </p>
          </div>
          <div className="principle">
            <h3>Accountability</h3>
            <p>
              Everyone owns the quality of the work they produce. When you ship it, you stand
              behind it. AI assists, humans are accountable.
            </p>
          </div>
          <div className="principle">
            <h3>Reliability</h3>
            <p>
              Our software works consistently, predictably, and under extreme pressure. If it can
              break, we find out before our users do.
            </p>
          </div>
          <div className="principle">
            <h3>Transparency</h3>
            <p>
              Evidence-backed functionality, no black boxes. Our processes, our standards, and our
              reasoning are open for inspection.
            </p>
          </div>
          <div className="principle">
            <h3>Quality Is Not Negotiable</h3>
            <p>
              We don't trade quality for speed. Shortcuts create debt. Doing it right the first
              time is faster than fixing it later.
            </p>
          </div>
          <div className="principle">
            <h3>Community</h3>
            <p>
              We care, we share, and we give back. This handbook is open because the best practices
              shouldn't be gatekept.
            </p>
          </div>
        </div>
      </section>

      <section className="docs-section">
        <h2>Handbook</h2>
        <p>Browse the docs, discuss specific sections, and propose changes — all in one place.</p>
        {isLoading ? (
          <p>Loading...</p>
        ) : documents && documents.length > 0 ? (
          <div className="docs-grid">
            {documents.map((doc) => (
              <Link to={`/docs/${doc.slug}`} key={doc.slug} className="doc-card">
                <h3>{doc.title}</h3>
              </Link>
            ))}
          </div>
        ) : (
          <p>
            No documents synced yet. Push to the handbook repo or trigger a manual sync to get
            started.
          </p>
        )}
      </section>
    </div>
  );
}
