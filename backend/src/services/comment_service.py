"""Comment service for creating, reading, and managing threaded comments."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.comment import Comment
from src.models.document import Document
from src.models.section import Section


async def get_section_by_slug_and_anchor(
    db: AsyncSession,
    slug: str,
    anchor: str,
) -> Section | None:
    """Look up a section by its parent document slug and anchor.

    Args:
        db: Database session.
        slug: Document slug.
        anchor: Section anchor within the document.

    Returns:
        The Section if found, None otherwise.
    """
    stmt = select(Section).join(Document).where(Document.slug == slug, Section.anchor == anchor)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_comments_for_section(
    db: AsyncSession,
    section_id,
) -> list[Comment]:
    """Fetch all top-level comments with replies for a section.

    Args:
        db: Database session.
        section_id: UUID of the section.

    Returns:
        Top-level comments with their replies eagerly loaded.
    """
    stmt = (
        select(Comment)
        .where(Comment.section_id == section_id, Comment.parent_id.is_(None))
        .options(selectinload(Comment.replies).selectinload(Comment.author))
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_comment(
    db: AsyncSession,
    section_id,
    author_id,
    body: str,
    parent_id=None,
) -> Comment:
    """Create a new comment or reply on a section.

    Args:
        db: Database session.
        section_id: UUID of the section to comment on.
        author_id: UUID of the comment author.
        body: Comment text in markdown.
        parent_id: UUID of the parent comment if this is a reply.

    Returns:
        The created Comment instance.
    """
    comment = Comment(
        section_id=section_id,
        author_id=author_id,
        body=body,
        parent_id=parent_id,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment, attribute_names=["author"])
    return comment


async def update_comment(
    db: AsyncSession,
    comment: Comment,
    body: str,
) -> Comment:
    """Update the body of an existing comment.

    Args:
        db: Database session.
        comment: The comment to update.
        body: New comment text.

    Returns:
        The updated Comment instance.
    """
    comment.body = body
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(db: AsyncSession, comment: Comment) -> None:
    """Delete a comment and its replies.

    Args:
        db: Database session.
        comment: The comment to delete.
    """
    await db.delete(comment)
    await db.commit()


async def resolve_comment(db: AsyncSession, comment: Comment) -> Comment:
    """Mark a comment thread as resolved.

    Args:
        db: Database session.
        comment: The top-level comment to resolve.

    Returns:
        The updated Comment with is_resolved=True.
    """
    comment.is_resolved = True
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comment_by_id(db: AsyncSession, comment_id) -> Comment | None:
    """Fetch a single comment by ID with author loaded.

    Args:
        db: Database session.
        comment_id: UUID of the comment.

    Returns:
        The Comment if found, None otherwise.
    """
    stmt = select(Comment).where(Comment.id == comment_id).options(selectinload(Comment.author))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_comment_count_for_section(db: AsyncSession, section_id) -> int:
    """Count total comments (including replies) for a section.

    Args:
        db: Database session.
        section_id: UUID of the section.

    Returns:
        The total number of comments.
    """
    stmt = select(func.count(Comment.id)).where(Comment.section_id == section_id)
    result = await db.execute(stmt)
    return result.scalar_one()
