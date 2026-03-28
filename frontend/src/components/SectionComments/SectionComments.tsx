/**
 * Threaded comments panel for a document section.
 *
 * Displays existing comment threads and a composer for new comments.
 * Expandable/collapsible per section, with reply support.
 *
 * @module components/SectionComments
 */

import { useState } from "react";
import { useComments, useCreateComment } from "@/hooks/useComments";
import { useAuth } from "@/contexts/AuthContext";
import { CommentComposer } from "@/components/CommentComposer";
import type { CommentResponse } from "@/types/comments";
import "./SectionComments.css";

/** Props for the {@link SectionComments} component. */
interface SectionCommentsProps {
  /** Document slug. */
  slug: string;
  /** Section anchor for fetching comments. */
  anchor: string;
  /** Number of existing comments (for the toggle label). */
  commentCount: number;
}

/**
 * Expandable comment panel for a single document section.
 *
 * Shows a toggle button with the comment count. When expanded,
 * displays threaded comments and a composer for new comments.
 *
 * @example
 * ```tsx
 * <SectionComments slug="testing" anchor="test-pyramid" commentCount={3} />
 * ```
 */
export function SectionComments({ slug, anchor, commentCount }: SectionCommentsProps) {
  const [expanded, setExpanded] = useState(false);
  const { data: threads, isLoading } = useComments(slug, anchor);
  const createComment = useCreateComment(slug, anchor);
  const { isAuthenticated, login } = useAuth();
  const [replyingTo, setReplyingTo] = useState<string | null>(null);

  return (
    <div className="section-comments">
      <button className="comments-toggle" onClick={() => setExpanded(!expanded)}>
        {expanded ? "Hide" : "Show"} discussion
        {commentCount > 0 && <span className="comment-count">({commentCount})</span>}
      </button>

      {expanded && (
        <div className="comments-panel">
          {isLoading ? (
            <p className="comments-loading">Loading comments...</p>
          ) : threads && threads.length > 0 ? (
            <div className="comment-threads">
              {threads.map((thread) => (
                <div key={thread.id} className="comment-thread">
                  <CommentItem comment={thread} onReply={() => setReplyingTo(thread.id)} />
                  {thread.replies.map((reply) => (
                    <div key={reply.id} className="comment-reply">
                      <CommentItem comment={reply} />
                    </div>
                  ))}
                  {replyingTo === thread.id && isAuthenticated && (
                    <div className="reply-composer">
                      <CommentComposer
                        onSubmit={(body) => {
                          createComment.mutate({ body, parentId: thread.id });
                          setReplyingTo(null);
                        }}
                        onCancel={() => setReplyingTo(null)}
                        placeholder="Write a reply..."
                        isSubmitting={createComment.isPending}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="no-comments">No comments yet. Start the discussion.</p>
          )}

          {isAuthenticated ? (
            <CommentComposer
              onSubmit={(body) => createComment.mutate({ body })}
              placeholder="Add a comment..."
              isSubmitting={createComment.isPending}
            />
          ) : (
            <p className="login-prompt">
              <button onClick={login} className="btn-text">
                Sign in with GitHub
              </button>{" "}
              to join the discussion.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

/** Props for the {@link CommentItem} component. */
interface CommentItemProps {
  /** The comment to render. */
  comment: CommentResponse;
  /** Called when the user clicks "Reply". */
  onReply?: () => void;
}

/** Renders a single comment with author, timestamp, and reply button. */
function CommentItem({ comment, onReply }: CommentItemProps) {
  return (
    <div className="comment-item">
      <div className="comment-header">
        {comment.author.avatar_url && (
          <img src={comment.author.avatar_url} alt="" className="comment-avatar" />
        )}
        <strong>{comment.author.display_name}</strong>
        <span className="comment-time">{new Date(comment.created_at).toLocaleDateString()}</span>
      </div>
      <div className="comment-body">{comment.body}</div>
      {onReply && (
        <button className="btn-text comment-reply-btn" onClick={onReply}>
          Reply
        </button>
      )}
    </div>
  );
}
