"""Markdown section parser for splitting documents at heading boundaries.

Parses a markdown document into discrete sections based on H2 (##) and
H3 (###) headings. Each section captures the heading text, an anchor for
deep linking, the content between headings, and the parent-child
relationship between H2 and H3 sections.
"""

import re
import unicodedata
from dataclasses import dataclass

# Matches H2 and H3 headings at the start of a line
_HEADING_PATTERN = re.compile(r"^(#{2,3})\s+(.+)$", re.MULTILINE)


@dataclass
class ParsedSection:
    """A single parsed section from a markdown document.

    Attributes:
        anchor: URL-safe anchor derived from the heading text.
        title: The original heading text.
        heading_level: 2 for H2, 3 for H3.
        content: Markdown content belonging to this section (excluding the heading itself).
        sort_order: Position of this section within the document.
        parent_anchor: Anchor of the parent H2 section (for H3 sections), or None.
    """

    anchor: str
    title: str
    heading_level: int
    content: str
    sort_order: int
    parent_anchor: str | None


def generate_anchor(heading_text: str) -> str:
    """Generate a URL-safe anchor from a heading, matching GitHub's algorithm.

    Converts to lowercase, replaces spaces with hyphens, strips
    non-alphanumeric characters (except hyphens), and collapses
    consecutive hyphens.

    Args:
        heading_text: The raw heading text (e.g., "Solo Phase: AI-Assisted Review").

    Returns:
        A URL-safe anchor string (e.g., "solo-phase-ai-assisted-review").

    Example:
        >>> generate_anchor("Git & Branching")
        'git--branching'
        >>> generate_anchor("Solo Phase: AI-Assisted Review")
        'solo-phase-ai-assisted-review'
    """
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", heading_text)
    # Lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = text.replace(" ", "-")
    # Remove characters that aren't alphanumeric or hyphens
    text = re.sub(r"[^a-z0-9\-]", "", text)
    # Collapse consecutive hyphens
    text = re.sub(r"-{2,}", "-", text)
    # Strip leading/trailing hyphens
    text = text.strip("-")
    return text


def extract_title(markdown: str) -> str:
    r"""Extract the document title from the first H1 heading.

    Args:
        markdown: Raw markdown content.

    Returns:
        The title text, or "Untitled" if no H1 heading is found.

    Example:
        >>> extract_title("# Git & Branching\n\nSome content")
        'Git & Branching'
    """
    match = re.match(r"^#\s+(.+)$", markdown, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"


def parse_sections(markdown: str) -> list[ParsedSection]:
    r"""Parse a markdown document into sections split at H2 and H3 headings.

    Content before the first H2 heading (after the H1 title) is captured
    as an "intro" section with heading_level=2. Each subsequent H2 or H3
    heading starts a new section. H3 sections are linked to their parent
    H2 via the parent_anchor field.

    Args:
        markdown: Raw markdown content of the document.

    Returns:
        An ordered list of ParsedSection objects representing the
        document's structure.

    Example:
        >>> sections = parse_sections("# Title\n\nIntro text\n\n## Section One\n\nContent")
        >>> len(sections)
        2
        >>> sections[0].anchor
        'intro'
        >>> sections[1].title
        'Section One'
    """
    sections: list[ParsedSection] = []
    headings = list(_HEADING_PATTERN.finditer(markdown))

    # Find where the H1 title ends (content starts after the first line)
    h1_match = re.match(r"^#\s+.+$", markdown, re.MULTILINE)
    content_start = h1_match.end() if h1_match else 0

    # Determine the intro section (content between H1 and first H2/H3)
    first_heading_start = headings[0].start() if headings else len(markdown)
    intro_content = markdown[content_start:first_heading_start].strip()

    if intro_content:
        sections.append(
            ParsedSection(
                anchor="intro",
                title="Introduction",
                heading_level=2,
                content=intro_content,
                sort_order=0,
                parent_anchor=None,
            )
        )

    # Track the current H2 anchor for parenting H3 sections
    current_h2_anchor: str | None = None
    sort_offset = 1 if intro_content else 0

    # Track seen anchors to deduplicate (same as GitHub's behavior)
    seen_anchors: dict[str, int] = {}

    for i, match in enumerate(headings):
        hashes = match.group(1)
        heading_text = match.group(2).strip()
        level = len(hashes)
        anchor = generate_anchor(heading_text)

        # Deduplicate: append -1, -2, etc. for repeated anchors
        if anchor in seen_anchors:
            seen_anchors[anchor] += 1
            anchor = f"{anchor}-{seen_anchors[anchor]}"
        else:
            seen_anchors[anchor] = 0

        # Determine content: from end of this heading line to start of next heading
        content_start_pos = match.end()
        content_end_pos = headings[i + 1].start() if i + 1 < len(headings) else len(markdown)
        content = markdown[content_start_pos:content_end_pos].strip()

        if level == 2:
            current_h2_anchor = anchor
            parent = None
        else:
            parent = current_h2_anchor

        sections.append(
            ParsedSection(
                anchor=anchor,
                title=heading_text,
                heading_level=level,
                content=content,
                sort_order=i + sort_offset,
                parent_anchor=parent,
            )
        )

    return sections
