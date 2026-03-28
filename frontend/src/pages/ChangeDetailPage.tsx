/**
 * Page for viewing a pull request's details, diff, and review actions.
 *
 * @module pages/ChangeDetailPage
 */

import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/api/client";
import "./ChangeDetailPage.css";

/** Full PR details from the API. */
interface PRDetail {
  /** GitHub PR number. */
  number: number;
  /** PR title. */
  title: string;
  /** PR description. */
  body: string;
  /** GitHub login of the PR author. */
  author: string;
  /** PR state (open, closed, merged). */
  state: string;
  /** Unified diff of the changes. */
  diff: string;
  /** When the PR was opened. */
  created_at: string;
  /** Direct URL to the PR on GitHub. */
  url: string;
  /** Whether the PR can be merged. */
  mergeable: boolean | null;
}

/** View PR details with diff, review actions, and merge button. */
export function ChangeDetailPage() {
  const { prNumber } = useParams<{ prNumber: string }>();
  const [reviewBody, setReviewBody] = useState("");
  const [actionStatus, setActionStatus] = useState<string | null>(null);

  const {
    data: pr,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["changes", prNumber],
    queryFn: () => apiFetch<PRDetail>(`/api/changes/${prNumber}`),
    enabled: !!prNumber,
  });

  if (isLoading) return <p>Loading...</p>;
  if (!pr) return <p>Pull request not found.</p>;

  async function submitReview(event: "APPROVE" | "REQUEST_CHANGES" | "COMMENT") {
    setActionStatus(null);
    try {
      await apiFetch(`/api/changes/${prNumber}/review`, {
        method: "POST",
        body: JSON.stringify({ event, body: reviewBody }),
      });
      setActionStatus(`Review submitted: ${event.toLowerCase().replace("_", " ")}`);
      setReviewBody("");
    } catch (err) {
      setActionStatus(err instanceof Error ? err.message : "Review failed");
    }
  }

  async function handleMerge() {
    setActionStatus(null);
    try {
      await apiFetch(`/api/changes/${prNumber}/merge`, { method: "POST" });
      setActionStatus("Merged successfully");
      refetch();
    } catch (err) {
      setActionStatus(err instanceof Error ? err.message : "Merge failed");
    }
  }

  return (
    <div className="change-detail">
      <div className="pr-header">
        <h1>
          #{pr.number}: {pr.title}
        </h1>
        <div className="pr-meta">
          <span className={`pr-state pr-state-${pr.state}`}>{pr.state}</span>
          <span>by {pr.author}</span>
          <span>{new Date(pr.created_at).toLocaleDateString()}</span>
          <a href={pr.url} target="_blank" rel="noopener noreferrer">
            View on GitHub
          </a>
        </div>
      </div>

      {pr.body && (
        <div className="pr-description">
          <p>{pr.body}</p>
        </div>
      )}

      <div className="diff-section">
        <h2>Changes</h2>
        <pre className="diff-content">{pr.diff}</pre>
      </div>

      {pr.state === "open" && (
        <div className="review-section">
          <h2>Review</h2>
          <textarea
            className="review-textarea"
            value={reviewBody}
            onChange={(e) => setReviewBody(e.target.value)}
            placeholder="Write your review comments..."
            rows={4}
          />
          <div className="review-actions">
            <button className="btn-approve" onClick={() => submitReview("APPROVE")}>
              Approve
            </button>
            <button
              className="btn-request-changes"
              onClick={() => submitReview("REQUEST_CHANGES")}
            >
              Request Changes
            </button>
            <button className="btn-comment" onClick={() => submitReview("COMMENT")}>
              Comment
            </button>
            <button className="btn-merge" onClick={handleMerge} disabled={!pr.mergeable}>
              Squash & Merge
            </button>
          </div>
          {actionStatus && <p className="action-status">{actionStatus}</p>}
        </div>
      )}
    </div>
  );
}
