"""Content sync service for pulling docs from GitHub into the database.

Handles both the webhook-triggered flow and startup seeding: fetch
markdown files from GitHub, parse them into sections, and upsert
into PostgreSQL.
"""

import logging
import re
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.github.client import GitHubClient
from src.models.document import Document
from src.models.section import Section
from src.models.sync_log import SyncLog
from src.services.markdown_parser import ParsedSection, extract_title, parse_sections

logger = logging.getLogger(__name__)


def _slug_from_filename(filename: str) -> str:
    """Derive a URL-friendly slug from a markdown filename.

    Args:
        filename: The filename (e.g., "git-branching.md").

    Returns:
        The slug (e.g., "git-branching").
    """
    return filename.removesuffix(".md")


def _parse_readme_doc_order(readme_content: str) -> dict[str, int]:
    """Extract document ordering from the README's table of contents.

    Parses the markdown table in the README to determine display order.
    Links in the table follow the pattern [Title](docs/slug.md).

    Args:
        readme_content: Raw markdown content of README.md.

    Returns:
        A dict mapping slug to sort_order (0-indexed).
    """
    order: dict[str, int] = {}
    # Match table rows with links to docs/
    pattern = re.compile(r"\[.+?\]\(docs/(.+?)\.md\)")
    for i, match in enumerate(pattern.finditer(readme_content)):
        slug = match.group(1)
        order[slug] = i
    return order


async def sync_from_github(
    db: AsyncSession,
    github: GitHubClient,
    commit_sha: str,
) -> int:
    """Sync all handbook documents from GitHub into the database.

    Fetches the docs/ directory listing and README from GitHub,
    then for each markdown file: fetches content, parses sections,
    and upserts the document and its sections.

    Args:
        db: Database session.
        github: Authenticated GitHub API client.
        commit_sha: The commit SHA that triggered this sync.

    Returns:
        The number of documents synced.

    Raises:
        Exception: Any error during sync is logged to sync_log.
    """
    sync_log = SyncLog(github_sha=commit_sha, status="started")
    db.add(sync_log)
    await db.commit()

    try:
        # Get document ordering from README
        readme_content = await github.get_file_content("README.md")
        doc_order = _parse_readme_doc_order(readme_content)

        # List all files in docs/
        contents = await github.get_repo_contents("docs")
        md_files = [f for f in contents if f["name"].endswith(".md")]

        files_updated = 0
        for file_info in md_files:
            filename = file_info["name"]
            slug = _slug_from_filename(filename)

            # Fetch raw content
            content = await github.get_file_content(f"docs/{filename}")
            title = extract_title(content)
            sort_order = doc_order.get(slug, 99)

            # Upsert document
            result = await db.execute(select(Document).where(Document.slug == slug))
            doc = result.scalar_one_or_none()

            if doc:
                doc.filename = filename
                doc.title = title
                doc.raw_markdown = content
                doc.github_sha = commit_sha
                doc.sort_order = sort_order
                doc.synced_at = datetime.now(timezone.utc)
            else:
                doc = Document(
                    slug=slug,
                    filename=filename,
                    title=title,
                    raw_markdown=content,
                    github_sha=commit_sha,
                    sort_order=sort_order,
                )
                db.add(doc)
                await db.flush()  # Get the doc.id assigned

            # Replace sections: delete old, insert new
            await db.execute(delete(Section).where(Section.document_id == doc.id))

            parsed = parse_sections(content)
            _insert_sections(db, doc.id, parsed)

            files_updated += 1

        await db.commit()

        # Update sync log
        sync_log.status = "completed"
        sync_log.files_updated = files_updated
        sync_log.completed_at = datetime.now(timezone.utc)
        await db.commit()

        return files_updated

    except Exception as e:
        sync_log.status = "failed"
        sync_log.error_message = str(e)
        sync_log.completed_at = datetime.now(timezone.utc)
        await db.commit()
        raise


def _insert_sections(
    db: AsyncSession,
    document_id,
    parsed_sections: list[ParsedSection],
) -> None:
    """Create Section ORM objects from parsed sections.

    Handles the parent-child relationship between H2 and H3 sections
    by tracking anchors to UUIDs.

    Args:
        db: Database session (sections are added but not committed).
        document_id: UUID of the parent document.
        parsed_sections: Ordered list of parsed sections from the markdown parser.
    """
    # Map anchor -> Section object for parent lookups
    anchor_to_section: dict[str, Section] = {}

    for parsed in parsed_sections:
        section = Section(
            document_id=document_id,
            anchor=parsed.anchor,
            title=parsed.title,
            heading_level=parsed.heading_level,
            content=parsed.content,
            sort_order=parsed.sort_order,
        )

        # Link H3 to parent H2
        if parsed.parent_anchor and parsed.parent_anchor in anchor_to_section:
            section.parent_section_id = anchor_to_section[parsed.parent_anchor].id

        db.add(section)
        anchor_to_section[parsed.anchor] = section


async def seed_if_empty(db: AsyncSession, github: GitHubClient) -> bool:
    """Seed the database with docs from GitHub if no documents exist.

    Called on app startup to ensure the DB is never empty on a fresh
    deploy or after a database reset. If documents already exist,
    this is a no-op.

    Args:
        db: Database session.
        github: GitHub API client configured for the handbook repo.

    Returns:
        True if seeding was performed, False if docs already existed.
    """
    result = await db.execute(select(func.count(Document.id)))
    count = result.scalar_one()

    if count > 0:
        logger.info("Database has %d documents, skipping seed", count)
        return False

    logger.info("Database is empty, seeding from GitHub...")
    try:
        commit_sha = await github.get_latest_commit_sha()
        files_updated = await sync_from_github(db, github, commit_sha)
        logger.info("Seed complete: %d documents synced", files_updated)
        return True
    except Exception:
        logger.exception("Seed from GitHub failed")
        return False
