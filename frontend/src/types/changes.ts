/** Abbreviated PR info for list views. */
export interface PRSummary {
  /** GitHub PR number. */
  number: number;
  /** PR title. */
  title: string;
  /** GitHub login of the PR author. */
  author: string;
  /** PR state (open, closed, merged). */
  state: string;
  /** When the PR was opened. */
  created_at: string;
  /** Direct URL to the PR on GitHub. */
  url: string;
}
