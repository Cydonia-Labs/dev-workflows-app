/**
 * Markdown comment input with submit/cancel actions.
 *
 * @module components/CommentComposer
 */

import { useState } from "react";
import "./CommentComposer.css";

/** Props for the {@link CommentComposer} component. */
interface CommentComposerProps {
  /** Called with the comment body when the user submits. */
  onSubmit: (body: string) => void;
  /** Called when the user cancels (optional — hides cancel button if absent). */
  onCancel?: () => void;
  /** Placeholder text for the textarea. */
  placeholder?: string;
  /** Whether a submission is in progress (disables the button). */
  isSubmitting?: boolean;
}

/**
 * A textarea with submit and optional cancel buttons for writing comments.
 *
 * Clears the input on successful submit. Disables interaction while
 * a submission is in progress.
 *
 * @example
 * ```tsx
 * <CommentComposer
 *   onSubmit={(body) => createComment(body)}
 *   placeholder="Add a comment..."
 * />
 * ```
 */
export function CommentComposer({
  onSubmit,
  onCancel,
  placeholder = "Write a comment...",
  isSubmitting = false,
}: CommentComposerProps) {
  const [body, setBody] = useState("");

  function handleSubmit() {
    const trimmed = body.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
    setBody("");
  }

  return (
    <div className="comment-composer">
      <textarea
        className="comment-textarea"
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder={placeholder}
        rows={3}
        disabled={isSubmitting}
      />
      <div className="composer-actions">
        {onCancel && (
          <button className="btn-text" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </button>
        )}
        <button
          className="btn-primary btn-small"
          onClick={handleSubmit}
          disabled={isSubmitting || !body.trim()}
        >
          {isSubmitting ? "Posting..." : "Comment"}
        </button>
      </div>
    </div>
  );
}
