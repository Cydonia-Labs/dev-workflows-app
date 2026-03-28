"""Routes for proposing, reviewing, and merging document changes via GitHub PRs."""

from fastapi import APIRouter, Depends

from src.config import get_settings
from src.dependencies import get_current_user
from src.github.client import GitHubClient
from src.models.user import User
from src.schemas.changes import (
    MergeResponse,
    PRDetail,
    ProposeChangeRequest,
    ProposeChangeResponse,
    PRSummary,
    ReviewResponse,
    SubmitReviewRequest,
)
from src.services.auth_service import get_decrypted_github_token
from src.services.change_service import (
    get_pr_detail,
    list_open_prs,
    merge_pr,
    propose_change,
    submit_review,
)

router = APIRouter(prefix="/api/changes", tags=["changes"])


def _get_github_client(user: User) -> GitHubClient:
    """Create a GitHubClient using the authenticated user's token.

    Args:
        user: The authenticated user with a stored GitHub token.

    Returns:
        A GitHubClient configured for the handbook repo.
    """
    settings = get_settings()
    return GitHubClient(
        token=get_decrypted_github_token(user),
        repo_owner=settings.github_repo_owner,
        repo_name=settings.github_repo_name,
    )


@router.post("/propose", status_code=201)
async def propose_document_change(
    body: ProposeChangeRequest,
    user: User = Depends(get_current_user),
) -> ProposeChangeResponse:
    """Create a GitHub branch and PR from an in-app document edit.

    Args:
        body: The edited document content and PR metadata.
        user: The authenticated user.

    Returns:
        The PR number, URL, and branch name.
    """
    github = _get_github_client(user)
    try:
        return await propose_change(
            github,
            document_slug=body.document_slug,
            title=body.title,
            description=body.description,
            updated_markdown=body.updated_markdown,
        )
    finally:
        await github.close()


@router.get("")
async def list_changes(
    user: User = Depends(get_current_user),
) -> list[PRSummary]:
    """List open pull requests for the handbook repo.

    Args:
        user: The authenticated user.

    Returns:
        A list of open PR summaries.
    """
    github = _get_github_client(user)
    try:
        return await list_open_prs(github)
    finally:
        await github.close()


@router.get("/{pr_number}")
async def get_change_detail(
    pr_number: int,
    user: User = Depends(get_current_user),
) -> PRDetail:
    """Get full details of a pull request including its diff.

    Args:
        pr_number: The GitHub PR number.
        user: The authenticated user.

    Returns:
        Full PR details with diff content.
    """
    github = _get_github_client(user)
    try:
        return await get_pr_detail(github, pr_number)
    finally:
        await github.close()


@router.post("/{pr_number}/review")
async def submit_pr_review(
    pr_number: int,
    body: SubmitReviewRequest,
    user: User = Depends(get_current_user),
) -> ReviewResponse:
    """Submit a review on a handbook PR.

    Uses the authenticated user's GitHub token so the review
    appears as their review on GitHub.

    Args:
        pr_number: The GitHub PR number.
        body: Review action and comment.
        user: The authenticated user.

    Returns:
        The review ID and state.
    """
    github = _get_github_client(user)
    try:
        result = await submit_review(github, pr_number, body.event, body.body)
        return ReviewResponse(id=result["id"], state=result["state"])
    finally:
        await github.close()


@router.post("/{pr_number}/merge")
async def merge_change(
    pr_number: int,
    user: User = Depends(get_current_user),
) -> MergeResponse:
    """Merge a handbook PR using squash merge.

    Args:
        pr_number: The GitHub PR number.
        user: The authenticated user.

    Returns:
        The merge commit SHA and success status.
    """
    github = _get_github_client(user)
    try:
        return await merge_pr(github, pr_number)
    finally:
        await github.close()
