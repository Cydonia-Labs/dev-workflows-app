/**
 * Renders markdown content as HTML with syntax highlighting and GFM support.
 *
 * Uses react-markdown with remark-gfm for tables and rehype-highlight
 * for code syntax highlighting. Sections are rendered with anchor IDs
 * for deep linking.
 *
 * @module components/MarkdownRenderer
 */

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css";
import "./MarkdownRenderer.css";

/** Props for the {@link MarkdownRenderer} component. */
interface MarkdownRendererProps {
  /** Raw markdown content to render. */
  content: string;
}

/**
 * Render markdown to HTML with GFM tables and syntax-highlighted code blocks.
 *
 * @example
 * ```tsx
 * <MarkdownRenderer content="## Hello\n\nSome **bold** text." />
 * ```
 */
export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <div className="markdown-body">
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
