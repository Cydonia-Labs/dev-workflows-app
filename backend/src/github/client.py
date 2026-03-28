"""Async GitHub REST API client.

Wraps httpx.AsyncClient for all GitHub API interactions. Each instance
is bound to a specific user's OAuth token so actions are attributed
correctly on GitHub.
"""

import base64
import uuid

import httpx

# Base URL for the GitHub REST API v3
GITHUB_API_BASE = "https://api.github.com"


class GitHubClient:
    """Async client for the GitHub REST API.

    Uses the authenticated user's OAuth token for all requests so
    actions (PRs, reviews, merges) appear as that user on GitHub.

    Attributes:
        token: OAuth access token for authentication.
        repo_owner: GitHub username or org that owns the target repo.
        repo_name: Name of the target repository.
    """

    def __init__(self, token: str, repo_owner: str, repo_name: str) -> None:
        """Initialize the GitHub client.

        Args:
            token: GitHub OAuth access token.
            repo_owner: Repository owner (user or org).
            repo_name: Repository name.
        """
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self._client = httpx.AsyncClient(
            base_url=GITHUB_API_BASE,
            headers=headers,
            timeout=30.0,
        )

    @property
    def _repo_path(self) -> str:
        """Build the /repos/{owner}/{repo} path prefix.

        Returns:
            The repository API path prefix.
        """
        return f"/repos/{self.repo_owner}/{self.repo_name}"

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def get_user(self) -> dict:
        """Fetch the authenticated user's GitHub profile.

        Returns:
            A dict with id, login, name, avatar_url, etc.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        response = await self._client.get("/user")
        response.raise_for_status()
        return response.json()

    async def get_repo_contents(self, path: str, ref: str = "main") -> list[dict]:
        """List files in a repository directory.

        Args:
            path: Directory path within the repo (e.g., "docs").
            ref: Git ref to read from. Defaults to "main".

        Returns:
            A list of file/directory metadata dicts.

        Raises:
            httpx.HTTPStatusError: If the path doesn't exist or the request fails.
        """
        response = await self._client.get(
            f"{self._repo_path}/contents/{path}",
            params={"ref": ref},
        )
        response.raise_for_status()
        return response.json()

    async def get_file_content(self, path: str, ref: str = "main") -> str:
        """Fetch the raw content of a file from the repository.

        Args:
            path: File path within the repo (e.g., "docs/testing.md").
            ref: Git ref to read from. Defaults to "main".

        Returns:
            The raw file content as a string.

        Raises:
            httpx.HTTPStatusError: If the file doesn't exist or the request fails.
        """
        response = await self._client.get(
            f"{self._repo_path}/contents/{path}",
            params={"ref": ref},
            headers={"Accept": "application/vnd.github.raw"},
        )
        response.raise_for_status()
        return response.text

    async def get_file_sha(self, path: str, ref: str = "main") -> str:
        """Get the blob SHA of a file (needed for updating file content).

        Args:
            path: File path within the repo.
            ref: Git ref to read from. Defaults to "main".

        Returns:
            The file's blob SHA.

        Raises:
            httpx.HTTPStatusError: If the file doesn't exist or the request fails.
        """
        response = await self._client.get(
            f"{self._repo_path}/contents/{path}",
            params={"ref": ref},
        )
        response.raise_for_status()
        return response.json()["sha"]

    async def get_ref_sha(self, ref: str = "heads/main") -> str:
        """Get the commit SHA for a git ref.

        Args:
            ref: The ref to look up (e.g., "heads/main").

        Returns:
            The commit SHA.

        Raises:
            httpx.HTTPStatusError: If the ref doesn't exist.
        """
        response = await self._client.get(f"{self._repo_path}/git/ref/{ref}")
        response.raise_for_status()
        return response.json()["object"]["sha"]

    async def create_branch(self, branch_name: str, from_sha: str) -> dict:
        """Create a new branch from a given commit SHA.

        Args:
            branch_name: Name of the new branch (without refs/heads/ prefix).
            from_sha: The commit SHA to branch from.

        Returns:
            The created ref object.

        Raises:
            httpx.HTTPStatusError: If the branch already exists or creation fails.
        """
        response = await self._client.post(
            f"{self._repo_path}/git/refs",
            json={"ref": f"refs/heads/{branch_name}", "sha": from_sha},
        )
        response.raise_for_status()
        return response.json()

    async def update_file(
        self,
        path: str,
        content: str,
        file_sha: str,
        branch: str,
        message: str,
    ) -> dict:
        """Update a file's content on a specific branch.

        Args:
            path: File path within the repo.
            content: New file content (will be base64-encoded).
            file_sha: Current blob SHA of the file (for conflict detection).
            branch: Branch to commit to.
            message: Commit message.

        Returns:
            The commit and content metadata.

        Raises:
            httpx.HTTPStatusError: If the update fails (e.g., SHA mismatch).
        """
        encoded_content = base64.b64encode(content.encode()).decode()
        response = await self._client.put(
            f"{self._repo_path}/contents/{path}",
            json={
                "message": message,
                "content": encoded_content,
                "sha": file_sha,
                "branch": branch,
            },
        )
        response.raise_for_status()
        return response.json()

    async def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
    ) -> dict:
        """Open a pull request.

        Args:
            title: PR title.
            body: PR description (markdown).
            head: Source branch name.
            base: Target branch name. Defaults to "main".

        Returns:
            The created pull request object.

        Raises:
            httpx.HTTPStatusError: If PR creation fails.
        """
        response = await self._client.post(
            f"{self._repo_path}/pulls",
            json={"title": title, "body": body, "head": head, "base": base},
        )
        response.raise_for_status()
        return response.json()

    async def list_pull_requests(self, state: str = "open") -> list[dict]:
        """List pull requests for the repository.

        Args:
            state: Filter by PR state ("open", "closed", "all"). Defaults to "open".

        Returns:
            A list of pull request objects.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        response = await self._client.get(
            f"{self._repo_path}/pulls",
            params={"state": state},
        )
        response.raise_for_status()
        return response.json()

    async def get_pull_request(self, pr_number: int) -> dict:
        """Get details of a specific pull request.

        Args:
            pr_number: The PR number.

        Returns:
            The pull request object with full details.

        Raises:
            httpx.HTTPStatusError: If the PR doesn't exist.
        """
        response = await self._client.get(f"{self._repo_path}/pulls/{pr_number}")
        response.raise_for_status()
        return response.json()

    async def get_pr_diff(self, pr_number: int) -> str:
        """Get the diff for a pull request.

        Args:
            pr_number: The PR number.

        Returns:
            The unified diff as a string.

        Raises:
            httpx.HTTPStatusError: If the PR doesn't exist.
        """
        response = await self._client.get(
            f"{self._repo_path}/pulls/{pr_number}",
            headers={"Accept": "application/vnd.github.diff"},
        )
        response.raise_for_status()
        return response.text

    async def get_pr_comments(self, pr_number: int) -> list[dict]:
        """Get review comments on a pull request.

        Args:
            pr_number: The PR number.

        Returns:
            A list of review comment objects.

        Raises:
            httpx.HTTPStatusError: If the PR doesn't exist.
        """
        response = await self._client.get(
            f"{self._repo_path}/pulls/{pr_number}/comments"
        )
        response.raise_for_status()
        return response.json()

    async def submit_review(
        self,
        pr_number: int,
        event: str,
        body: str,
    ) -> dict:
        """Submit a review on a pull request.

        Args:
            pr_number: The PR number.
            event: Review action ("APPROVE", "REQUEST_CHANGES", "COMMENT").
            body: Review comment body.

        Returns:
            The created review object.

        Raises:
            httpx.HTTPStatusError: If the review submission fails.
        """
        response = await self._client.post(
            f"{self._repo_path}/pulls/{pr_number}/reviews",
            json={"event": event, "body": body},
        )
        response.raise_for_status()
        return response.json()

    async def merge_pull_request(
        self,
        pr_number: int,
        merge_method: str = "squash",
    ) -> dict:
        """Merge a pull request.

        Args:
            pr_number: The PR number.
            merge_method: Merge strategy ("merge", "squash", "rebase").
                Defaults to "squash".

        Returns:
            The merge result with sha and merged status.

        Raises:
            httpx.HTTPStatusError: If the merge fails (e.g., conflicts).
        """
        response = await self._client.put(
            f"{self._repo_path}/pulls/{pr_number}/merge",
            json={"merge_method": merge_method},
        )
        response.raise_for_status()
        return response.json()

    async def get_latest_commit_sha(self, ref: str = "main") -> str:
        """Get the latest commit SHA for a branch.

        Args:
            ref: Branch name. Defaults to "main".

        Returns:
            The latest commit SHA.

        Raises:
            httpx.HTTPStatusError: If the branch doesn't exist.
        """
        response = await self._client.get(
            f"{self._repo_path}/commits/{ref}",
        )
        response.raise_for_status()
        return response.json()["sha"]
