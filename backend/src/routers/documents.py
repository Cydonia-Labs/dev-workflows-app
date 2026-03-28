"""Document browsing routes."""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models.document import Document
from src.models.section import Section
from src.schemas.documents import DocumentDetail, DocumentSummary, SectionResponse
from src.services.comment_service import get_comment_count_for_section

router = APIRouter(prefix="/api/docs", tags=["documents"])


@router.get("")
async def list_documents(
    db: AsyncSession = Depends(get_db),
) -> list[DocumentSummary]:
    """Return all handbook documents ordered by display position.

    Args:
        db: Database session.

    Returns:
        A list of document summaries.
    """
    stmt = select(Document).order_by(Document.sort_order)
    result = await db.execute(stmt)
    docs = result.scalars().all()
    return [
        DocumentSummary(slug=d.slug, title=d.title, sort_order=d.sort_order)
        for d in docs
    ]


@router.get("/{slug}")
async def get_document(
    slug: str = Path(max_length=100, pattern=r"^[a-z0-9\-]+$"),
    db: AsyncSession = Depends(get_db),
) -> DocumentDetail:
    """Return a document with its parsed sections.

    Args:
        slug: URL-friendly document identifier.
        db: Database session.

    Returns:
        Full document detail with sections and comment counts.

    Raises:
        HTTPException(404): If no document matches the slug.
    """
    stmt = (
        select(Document)
        .where(Document.slug == slug)
        .options(selectinload(Document.sections))
    )
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()

    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    sections = []
    for s in sorted(doc.sections, key=lambda x: x.sort_order):
        count = await get_comment_count_for_section(db, s.id)
        sections.append(
            SectionResponse(
                id=str(s.id),
                anchor=s.anchor,
                title=s.title,
                heading_level=s.heading_level,
                content=s.content,
                sort_order=s.sort_order,
                comment_count=count,
            )
        )

    return DocumentDetail(
        slug=doc.slug,
        title=doc.title,
        raw_markdown=doc.raw_markdown,
        sections=sections,
        github_sha=doc.github_sha,
        synced_at=doc.synced_at,
    )


@router.get("/{slug}/sections/{anchor}")
async def get_section(
    slug: str = Path(max_length=100, pattern=r"^[a-z0-9\-]+$"),
    anchor: str = Path(max_length=255, pattern=r"^[a-z0-9\-]+$"),
    db: AsyncSession = Depends(get_db),
) -> SectionResponse:
    """Return a single section from a document.

    Args:
        slug: Document slug.
        anchor: Section anchor within the document.
        db: Database session.

    Returns:
        The section with comment count.

    Raises:
        HTTPException(404): If the document or section is not found.
    """
    stmt = (
        select(Section)
        .join(Document)
        .where(Document.slug == slug, Section.anchor == anchor)
    )
    result = await db.execute(stmt)
    section = result.scalar_one_or_none()

    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")

    count = await get_comment_count_for_section(db, section.id)

    return SectionResponse(
        id=str(section.id),
        anchor=section.anchor,
        title=section.title,
        heading_level=section.heading_level,
        content=section.content,
        sort_order=section.sort_order,
        comment_count=count,
    )
