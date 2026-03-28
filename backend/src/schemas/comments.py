"""Pydantic schemas for comment endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.auth import UserResponse


class CreateCommentRequest(BaseModel):
    """Request body for creating a new comment or reply.

    Attributes:
        body: Comment text in markdown.
        parent_id: If set, this comment is a reply to the specified comment.
    """

    body: str = Field(min_length=1, max_length=10000)
    parent_id: str | None = None


class UpdateCommentRequest(BaseModel):
    """Request body for editing an existing comment.

    Attributes:
        body: Updated comment text in markdown.
    """

    body: str = Field(min_length=1, max_length=10000)


class CommentResponse(BaseModel):
    """A single comment with author info.

    Attributes:
        id: Comment unique identifier.
        author: The user who wrote the comment.
        body: Comment text in markdown.
        parent_id: Parent comment ID if this is a reply.
        is_resolved: Whether this thread is marked as resolved.
        created_at: When the comment was posted.
        updated_at: When the comment was last edited.
    """

    id: str
    author: UserResponse
    body: str
    parent_id: str | None
    is_resolved: bool
    created_at: datetime
    updated_at: datetime


class CommentThread(CommentResponse):
    """A top-level comment with its nested replies.

    Attributes:
        replies: Child comments in chronological order.
    """

    replies: list[CommentResponse] = []
