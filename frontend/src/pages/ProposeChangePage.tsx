/**
 * Page for proposing a documentation change via in-app markdown editor.
 *
 * Loads the current document content, provides an editor with live
 * preview, and submits the change as a GitHub PR.
 *
 * @module pages/ProposeChangePage
 */

import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useDocument } from "@/hooks/useDocuments";
import { apiFetch } from "@/api/client";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import "./ProposeChangePage.css";

/** Response from the propose change endpoint. */
interface ProposeResponse {
  /** GitHub PR number. */
  pr_number: number;
  /** Direct URL to the PR on GitHub. */
  pr_url: string;
  /** Branch name created for the change. */
  branch: string;
}

/** Edit a handbook document and submit the change as a GitHub PR. */
export function ProposeChangePage() {
  const [searchParams] = useSearchParams();
  const slug = searchParams.get("doc") ?? "";
  const navigate = useNavigate();
  const { data: doc, isLoading } = useDocument(slug);

  const [markdown, setMarkdown] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [showPreview, setShowPreview] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize editor content from the document once loaded
  if (doc && markdown === null) {
    setMarkdown(doc.raw_markdown);
  }

  if (isLoading) return <p>Loading document...</p>;
  if (!doc) return <p>Document not found.</p>;

  async function handleSubmit() {
    if (!title.trim() || !markdown) return;
    setSubmitting(true);
    setError(null);

    try {
      const result = await apiFetch<ProposeResponse>("/api/changes/propose", {
        method: "POST",
        body: JSON.stringify({
          document_slug: slug,
          title: title.trim(),
          description: description.trim(),
          updated_markdown: markdown,
        }),
      });
      navigate(`/changes`, { state: { created: result.pr_number } });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create PR");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="propose-change">
      <h1>Propose Change to: {doc.title}</h1>

      <div className="propose-form">
        <input
          className="propose-title"
          type="text"
          placeholder="Change title (e.g., docs(testing): add Playwright E2E examples)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
        />

        <textarea
          className="propose-description"
          placeholder="Describe what you're changing and why..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
        />

        <div className="editor-toolbar">
          <button
            className={`tab-btn ${!showPreview ? "active" : ""}`}
            onClick={() => setShowPreview(false)}
          >
            Edit
          </button>
          <button
            className={`tab-btn ${showPreview ? "active" : ""}`}
            onClick={() => setShowPreview(true)}
          >
            Preview
          </button>
        </div>

        {showPreview ? (
          <div className="editor-preview">
            <MarkdownRenderer content={markdown ?? ""} />
          </div>
        ) : (
          <textarea
            className="editor-textarea"
            value={markdown ?? ""}
            onChange={(e) => setMarkdown(e.target.value)}
            rows={30}
          />
        )}

        {error && <p className="error-message">{error}</p>}

        <div className="propose-actions">
          <button className="btn-text" onClick={() => navigate(-1)} disabled={submitting}>
            Cancel
          </button>
          <button
            className="btn-primary"
            onClick={handleSubmit}
            disabled={submitting || !title.trim()}
          >
            {submitting ? "Creating PR..." : "Submit Change"}
          </button>
        </div>
      </div>
    </div>
  );
}
