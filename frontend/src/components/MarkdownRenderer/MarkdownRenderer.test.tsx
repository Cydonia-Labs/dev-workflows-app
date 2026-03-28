import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MarkdownRenderer } from "./MarkdownRenderer";

describe("MarkdownRenderer", () => {
  it("renders markdown text as HTML", () => {
    render(<MarkdownRenderer content="Hello **world**" />);
    expect(screen.getByText("world")).toBeInTheDocument();
  });

  it("renders headings", () => {
    render(<MarkdownRenderer content="## Section Title" />);
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("Section Title");
  });

  it("renders code blocks", () => {
    render(<MarkdownRenderer content={'```python\nprint("hi")\n```'} />);
    expect(screen.getByText(/print/)).toBeInTheDocument();
  });

  it("renders tables from GFM", () => {
    const md = "| A | B |\n|---|---|\n| 1 | 2 |";
    render(<MarkdownRenderer content={md} />);
    expect(screen.getByRole("table")).toBeInTheDocument();
  });
});
