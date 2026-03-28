"""Comment routes for threaded discussions on document sections."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.auth import UserResponse
from src.schemas.comments import (
    CommentResponse,
    CommentThread,
    CreateCommentRequest,
    UpdateCommentRequest,
)
from src.services.comment_service import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    get_comments_for_section,
    get_section_by_slug_and_anchor,
    resolve_comment,
    update_comment,
)

router = APIRouter(tags=["comments"])


def _comment_to_response(comment) -> CommentResponse:
    """Convert a Comment ORM object to a CommentResponse schema.

    Args:
        comment: Comment ORM instance with author loaded.

    Returns:
        A CommentResponse with the author's public profile.
    """
    return CommentResponse(
        id=str(comment.id),
        author=UserResponse(
            id=str(comment.author.id),
            github_login=comment.author.github_login,
            display_name=comment.author.display_name,
            avatar_url=comment.author.avatar_url,
        ),
        body=comment.body,
        parent_id=str(comment.parent_id) if comment.parent_id else None,
        is_resolved=comment.is_resolved,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.get("/api/docs/{slug}/sections/{anchor}/comments")
async def list_comments(
    slug: str,
    anchor: str,
    db: AsyncSession = Depends(get_db),
) -> list[CommentThread]:
    """Return threaded comments for a document section.

    Args:
        slug: Document slug.
        anchor: Section anchor.
        db: Database session.

    Returns:
        Top-level comments with their nested replies.

    Raises:
        HTTPException(404): If the section is not found.
    """
    section = await get_section_by_slug_and_anchor(db, slug, anchor)
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")

    comments = await get_comments_for_section(db, section.id)
    return [
        CommentThread(
            **_comment_to_response(c).model_dump(),
            replies=[_comment_to_response(r) for r in c.replies],
        )
        for c in comments
    ]


@router.post("/api/docs/{slug}/sections/{anchor}/comments", status_code=201)
async def create_new_comment(
    slug: str,
    anchor: str,
    body: CreateCommentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    """Create a new comment or reply on a document section.

    Args:
        slug: Document slug.
        anchor: Section anchor.
        body: Comment content and optional parent_id.
        user: The authenticated user.
        db: Database session.

    Returns:
        The created comment.

    Raises:
        HTTPException(404): If the section is not found.
    """
    section = await get_section_by_slug_and_anchor(db, slug, anchor)
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")

    comment = await create_comment(
        db,
        section_id=section.id,
        author_id=user.id,
        body=body.body,
        parent_id=body.parent_id,
    )
    return _comment_to_response(comment)


@router.patch("/api/comments/{comment_id}")
async def edit_comment(
    comment_id: str,
    body: UpdateCommentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    """Edit an existing comment (author only).

    Args:
        comment_id: UUID of the comment to edit.
        body: Updated comment text.
        user: The authenticated user.
        db: Database session.

    Returns:
        The updated comment.

    Raises:
        HTTPException(404): If the comment is not found.
        HTTPException(403): If the user is not the comment author.
    """
    comment = await get_comment_by_id(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not your comment")

    updated = await update_comment(db, comment, body.body)
    return _comment_to_response(updated)


@router.delete("/api/comments/{comment_id}", status_code=204)
async def remove_comment(
    comment_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a comment (author only).

    Args:
        comment_id: UUID of the comment to delete.
        user: The authenticated user.
        db: Database session.

    Raises:
        HTTPException(404): If the comment is not found.
        HTTPException(403): If the user is not the comment author.
    """
    comment = await get_comment_by_id(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not your comment")

    await delete_comment(db, comment)


@router.post("/api/comments/{comment_id}/resolve")
async def resolve_thread(
    comment_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    """Mark a comment thread as resolved.

    Args:
        comment_id: UUID of the top-level comment to resolve.
        user: The authenticated user.
        db: Database session.

    Returns:
        The resolved comment.

    Raises:
        HTTPException(404): If the comment is not found.
    """
    comment = await get_comment_by_id(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    resolved = await resolve_comment(db, comment)
    return _comment_to_response(resolved)
