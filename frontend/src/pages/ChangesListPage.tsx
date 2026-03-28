/**
 * Page listing open pull requests for the handbook.
 *
 * @module pages/ChangesListPage
 */

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/api/client";
import type { PRSummary } from "@/types/changes";

/** List open PRs for the handbook repo. */
export function ChangesListPage() {
  const { data: changes, isLoading } = useQuery({
    queryKey: ["changes"],
    queryFn: () => apiFetch<PRSummary[]>("/api/changes"),
  });

  if (isLoading) return <p>Loading changes...</p>;

  return (
    <div>
      <h1>Open Changes</h1>
      {changes && changes.length > 0 ? (
        <ul>
          {changes.map((pr) => (
            <li key={pr.number}>
              <a href={pr.url} target="_blank" rel="noopener noreferrer">
                #{pr.number}: {pr.title}
              </a>
              <span> by {pr.author}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p>No open changes.</p>
      )}
    </div>
  );
}
