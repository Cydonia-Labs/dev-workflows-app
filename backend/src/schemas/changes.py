"""Pydantic schemas for change proposal and PR management endpoints."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ProposeChangeRequest(BaseModel):
    """Request body for proposing a documentation change.

    Attributes:
        document_slug: Which document is being edited.
        title: PR title describing the change.
        description: PR body with context about the change.
        updated_markdown: The full updated markdown content.
    """

    document_slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9\-]+$")
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(max_length=5000)
    # 500 KB limit — handbook docs are typically 5-30 KB
    updated_markdown: str = Field(max_length=512_000)


class ProposeChangeResponse(BaseModel):
    """Response after successfully creating a change PR.

    Attributes:
        pr_number: The GitHub PR number.
        pr_url: Direct URL to the PR on GitHub.
        branch: The branch name created for this change.
    """

    pr_number: int
    pr_url: str
    branch: str


class SubmitReviewRequest(BaseModel):
    """Request body for submitting a review on a PR.

    Attributes:
        event: The review action to take.
        body: Review comment text.
    """

    event: Literal["APPROVE", "REQUEST_CHANGES", "COMMENT"]
    body: str = Field(max_length=10000)


class PRSummary(BaseModel):
    """Abbreviated PR info for list views.

    Attributes:
        number: GitHub PR number.
        title: PR title.
        author: GitHub login of the PR author.
        state: PR state (open, closed, merged).
        created_at: When the PR was opened.
        url: Direct URL to the PR on GitHub.
    """

    number: int
    title: str
    author: str
    state: str
    created_at: datetime
    url: str


class PRDetail(BaseModel):
    """Full PR details including diff.

    Attributes:
        number: GitHub PR number.
        title: PR title.
        body: PR description.
        author: GitHub login of the PR author.
        state: PR state.
        diff: Unified diff of the changes.
        created_at: When the PR was opened.
        url: Direct URL to the PR on GitHub.
        mergeable: Whether the PR can be merged.
    """

    number: int
    title: str
    body: str
    author: str
    state: str
    diff: str
    created_at: datetime
    url: str
    mergeable: bool | None


class ReviewResponse(BaseModel):
    """Response after submitting a review.

    Attributes:
        id: GitHub review ID.
        state: Review state (APPROVED, CHANGES_REQUESTED, COMMENTED).
    """

    id: int
    state: str


class MergeResponse(BaseModel):
    """Response after merging a PR.

    Attributes:
        sha: The merge commit SHA.
        merged: Whether the merge was successful.
    """

    sha: str
    merged: bool
