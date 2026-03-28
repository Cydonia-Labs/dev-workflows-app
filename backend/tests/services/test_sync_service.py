"""Tests for the content sync service helper functions."""

from src.services.sync_service import _parse_readme_doc_order, _slug_from_filename

# Note: seed_if_empty requires a real database session and GitHub API client,
# so it's tested via integration tests. Unit tests here cover the helper functions.


class TestSlugFromFilename:
    def test_removes_md_extension(self):
        assert _slug_from_filename("git-branching.md") == "git-branching"

    def test_handles_no_extension(self):
        assert _slug_from_filename("README") == "README"

    def test_handles_nested_dots(self):
        assert _slug_from_filename("ai-assisted-dev.md") == "ai-assisted-dev"


class TestParseReadmeDocOrder:
    def test_extracts_order_from_table(self):
        readme = """# Title

| Section | Description |
|---------|-------------|
| [Git & Branching](docs/git-branching.md) | Branch strategy |
| [Testing](docs/testing.md) | Test strategy |
| [CI/CD](docs/ci-cd.md) | Pipeline design |
"""
        order = _parse_readme_doc_order(readme)
        assert order == {"git-branching": 0, "testing": 1, "ci-cd": 2}

    def test_empty_readme(self):
        assert _parse_readme_doc_order("# No table here") == {}

    def test_ignores_non_docs_links(self):
        readme = "Check [CONTRIBUTING](CONTRIBUTING.md) and [Git](docs/git-branching.md)"
        order = _parse_readme_doc_order(readme)
        assert order == {"git-branching": 0}
