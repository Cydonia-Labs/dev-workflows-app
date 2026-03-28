"""Change service for managing document edit proposals via GitHub PRs."""

import uuid

from src.github.client import GitHubClient
from src.schemas.changes import MergeResponse, PRDetail, PRSummary, ProposeChangeResponse


async def propose_change(
    github: GitHubClient,
    document_slug: str,
    title: str,
    description: str,
    updated_markdown: str,
) -> ProposeChangeResponse:
    """Create a GitHub branch and PR from an in-app document edit.

    Flow:
    1. Get the current main branch SHA
    2. Create a new branch named docs/{slug}-{short_uuid}
    3. Get the current file SHA for conflict detection
    4. Commit the updated content to the new branch
    5. Open a PR against main

    Args:
        github: Authenticated GitHub client (uses the user's token).
        document_slug: Which document is being edited.
        title: PR title describing the change.
        description: PR body with context.
        updated_markdown: The full updated markdown content.

    Returns:
        PR number, URL, and branch name.

    Raises:
        httpx.HTTPStatusError: If any GitHub API call fails.
    """
    short_id = uuid.uuid4().hex[:8]
    branch_name = f"docs/{document_slug}-{short_id}"
    filename = f"docs/{document_slug}.md"

    # Get current main SHA
    main_sha = await github.get_ref_sha("heads/main")

    # Create branch
    await github.create_branch(branch_name, main_sha)

    # Get current file SHA for the update
    file_sha = await github.get_file_sha(filename)

    # Commit the change
    await github.update_file(
        path=filename,
        content=updated_markdown,
        file_sha=file_sha,
        branch=branch_name,
        message=title,
    )

    # Open PR
    pr = await github.create_pull_request(
        title=title,
        body=description,
        head=branch_name,
    )

    return ProposeChangeResponse(
        pr_number=pr["number"],
        pr_url=pr["html_url"],
        branch=branch_name,
    )


async def list_open_prs(github: GitHubClient) -> list[PRSummary]:
    """List open pull requests for the handbook repo.

    Args:
        github: Authenticated GitHub client.

    Returns:
        A list of PR summaries.
    """
    prs = await github.list_pull_requests(state="open")
    return [
        PRSummary(
            number=pr["number"],
            title=pr["title"],
            author=pr["user"]["login"],
            state=pr["state"],
            created_at=pr["created_at"],
            url=pr["html_url"],
        )
        for pr in prs
    ]


async def get_pr_detail(github: GitHubClient, pr_number: int) -> PRDetail:
    """Get full details of a pull request including its diff.

    Args:
        github: Authenticated GitHub client.
        pr_number: The PR number.

    Returns:
        Full PR details with diff.
    """
    pr = await github.get_pull_request(pr_number)
    diff = await github.get_pr_diff(pr_number)

    return PRDetail(
        number=pr["number"],
        title=pr["title"],
        body=pr.get("body") or "",
        author=pr["user"]["login"],
        state=pr["state"],
        diff=diff,
        created_at=pr["created_at"],
        url=pr["html_url"],
        mergeable=pr.get("mergeable"),
    )


async def submit_review(
    github: GitHubClient,
    pr_number: int,
    event: str,
    body: str,
) -> dict:
    """Submit a review on a pull request.

    Args:
        github: Authenticated GitHub client.
        pr_number: The PR number.
        event: Review action ("APPROVE", "REQUEST_CHANGES", "COMMENT").
        body: Review comment text.

    Returns:
        The GitHub review response.
    """
    return await github.submit_review(pr_number, event, body)


async def merge_pr(github: GitHubClient, pr_number: int) -> MergeResponse:
    """Merge a pull request using squash merge.

    Args:
        github: Authenticated GitHub client.
        pr_number: The PR number.

    Returns:
        Merge result with SHA and success status.
    """
    result = await github.merge_pull_request(pr_number)
    return MergeResponse(sha=result["sha"], merged=result["merged"])
