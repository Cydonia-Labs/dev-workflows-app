"""Pydantic schemas for document and section endpoints."""

from datetime import datetime

from pydantic import BaseModel


class DocumentSummary(BaseModel):
    """Abbreviated document info for list views.

    Attributes:
        slug: URL-friendly document identifier.
        title: Document title from H1 heading.
        sort_order: Display ordering position.
    """

    slug: str
    title: str
    sort_order: int


class SectionResponse(BaseModel):
    """A parsed section within a document.

    Attributes:
        id: Section unique identifier.
        anchor: URL-safe anchor for deep linking.
        title: Section heading text.
        heading_level: 2 for H2, 3 for H3.
        content: Markdown content of the section.
        sort_order: Position within the document.
        comment_count: Number of comments on this section.
    """

    id: str
    anchor: str
    title: str
    heading_level: int
    content: str
    sort_order: int
    comment_count: int = 0


class DocumentDetail(BaseModel):
    """Full document with parsed sections.

    Attributes:
        slug: URL-friendly document identifier.
        title: Document title from H1 heading.
        raw_markdown: Full markdown content.
        sections: Parsed sections in display order.
        github_sha: Git commit SHA at last sync.
        synced_at: When the document was last synced.
    """

    slug: str
    title: str
    raw_markdown: str
    sections: list[SectionResponse]
    github_sha: str
    synced_at: datetime
