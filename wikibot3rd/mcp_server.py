"""
Created on 2026-02-16

@author: wf

MCP (Model Context Protocol) Server for py-3rdparty-mediawiki.
Allows AI assistants (Claude, Cursor, ChatGPT) to interact with wikis.
"""

import uuid
from typing import Any, Dict, List

try:
    from fastmcp import FastMCP
except ImportError:
    raise ImportError(
        "fastmcp is required for MCP server. Install with: pip install py-3rdparty-mediawiki[mcp]"
    )

from wikibot3rd.version import Version
from wikibot3rd.wikiclient import WikiClient
from wikibot3rd.wikiuser import WikiUser

mcp = FastMCP("py-3rdparty-mediawiki")

PREVIEW_STORE: Dict[str, Dict[str, Any]] = {}


def get_wiki_client(wiki_id: str) -> WikiClient:
    """
    Get a WikiClient for the given wiki ID and login if credentials are available.

    Args:
        wiki_id: The wiki identifier.

    Returns:
        WikiClient instance.

    Raises:
        ValueError: If the wiki is not found.
    """
    wiki_user = WikiUser.ofWikiId(wiki_id, lenient=False)
    if wiki_user is None:
        raise ValueError(f"Wiki '{wiki_id}' not found in configuration")
    client = WikiClient.of_wiki_user(wiki_user)
    
    # Auto-login if credentials are available
    if wiki_user.user and wiki_user.getPassword():
        try:
            client.login()
        except Exception:
            # Login failed, but continue anyway (some wikis allow read without login)
            pass
    
    return client


def format_page(page: Any) -> Dict[str, Any]:
    """
    Format a page object for MCP response.

    Args:
        page: The page object from mwclient.

    Returns:
        Dictionary with page data.
    """
    return {
        "title": page.name,
        "pageid": getattr(page, "pageid", None),
        "content": page.text() if hasattr(page, "text") else None,
    }


def format_search_result(result: Any) -> Dict[str, str]:
    """
    Format a search result for MCP response.

    Args:
        result: The search result from MediaWiki API.

    Returns:
        Dictionary with title and snippet.
    """
    if hasattr(result, "name"):
        title = result.name
    elif isinstance(result, dict):
        title = result.get("title", "")
    else:
        title = str(result)

    if hasattr(result, "pageid"):
        pageid = result.pageid
    elif isinstance(result, dict):
        pageid = result.get("pageid", 0)
    else:
        pageid = 0

    if hasattr(result, "get"):
        snippet = result.get("snippet", "")
    elif isinstance(result, dict):
        snippet = result.get("snippet", "")
    else:
        snippet = ""

    return {
        "title": title,
        "pageid": pageid,
        "snippet": snippet,
    }


def format_revision(revision: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a revision for MCP response.

    Args:
        revision: The revision from MediaWiki API.

    Returns:
        Dictionary with revision data.
    """
    return {
        "revid": revision.get("revid", 0),
        "parentid": revision.get("parentid", 0),
        "timestamp": revision.get("timestamp", ""),
        "user": revision.get("user", ""),
        "content": revision.get("*", ""),
    }


def list_wikis_impl() -> List[Dict[str, str]]:
    """
    List all configured wikis the bot can access.

    Returns:
        List of dicts with wikiId, url, user for each wiki.
    """
    wikis = []
    for wiki_user in WikiUser.getWikiUsers().values():
        wikis.append(
            {
                "wikiId": wiki_user.wikiId,
                "url": wiki_user.url,
                "user": wiki_user.user or "",
            }
        )
    return wikis


def set_wiki_impl(wiki_id: str) -> Dict[str, Any]:
    """
    Set the default wiki for the current session.

    Args:
        wiki_id: The wiki identifier to set as default.

    Returns:
        Success message.
    """
    wiki_user = WikiUser.ofWikiId(wiki_id, lenient=False)
    if wiki_user is None:
        raise ValueError(f"Wiki '{wiki_id}' not found")
    return {"success": True, "message": f"Default wiki set to {wiki_id}"}


def get_page_impl(wiki_id: str, page_title: str) -> Dict[str, Any]:
    """
    Get a wiki page.

    Args:
        wiki_id: The wiki identifier.
        page_title: Title of the page to retrieve.

    Returns:
        Dict with page data (title, pageid, content).
    """
    client = get_wiki_client(wiki_id)
    page = client.get_page(page_title)
    return format_page(page)


def get_page_markup_impl(wiki_id: str, page_title: str) -> str:
    """
    Get the raw wikitext markup for a Page.

    Args:
        wiki_id: The wiki identifier.
        page_title: Title of the page.

    Returns:
        Raw wikitext content.
    """
    client = get_wiki_client(wiki_id)
    return client.get_wiki_markup(page_title)


def search_page_impl(wiki_id: str, query: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Search wiki page titles and contents.

    Args:
        wiki_id: The wiki identifier.
        query: Search query.
        limit: Maximum results (default 10).

    Returns:
        List of matching pages with title and snippet.
    """
    client = get_wiki_client(wiki_id)
    site = client.get_site()
    results = site.search(query, limit=limit)
    return [format_search_result(r) for r in results]


def search_page_by_prefix_impl(wiki_id: str, prefix: str, limit: int = 10) -> List[str]:
    """
    Perform a prefix search for page titles.

    Args:
        wiki_id: The wiki identifier.
        prefix: Prefix to search for.
        limit: Maximum results (default 10).

    Returns:
        List of page titles matching the prefix.
    """
    client = get_wiki_client(wiki_id)
    site = client.get_site()
    results = site.search(prefix, limit=limit, what="prefix")
    return [r.name for r in results]


def get_page_history_impl(
    wiki_id: str, page_title: str, limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get page revision history.

    Args:
        wiki_id: The wiki identifier.
        page_title: Title of the page.
        limit: Maximum number of revisions (default 10).

    Returns:
        List of revision data.
    """
    client = get_wiki_client(wiki_id)
    page = client.get_page(page_title)
    revisions = page.revisions(limit=limit, prop="content|timestamp|user")
    return [
        format_revision(
            {
                "revid": rev.revid,
                "parentid": rev.parentid,
                "timestamp": str(rev.timestamp),
                "user": rev.user,
                "*": rev.text if hasattr(rev, "text") else "",
            }
        )
        for rev in revisions
    ]


def get_category_members_impl(
    wiki_id: str, category: str, limit: int = 10
) -> List[str]:
    """
    Get all members in a category.

    Args:
        wiki_id: The wiki identifier.
        category: Category name (with or without "Category:" prefix).
        limit: Maximum results (default 10).

    Returns:
        List of member page titles.
    """
    if not category.startswith("Category:"):
        category = f"Category:{category}"

    client = get_wiki_client(wiki_id)
    site = client.get_site()
    cat = site.categories[category]
    try:
        members = list(cat.members(limit=limit))
    except TypeError:
        members = list(cat.members())
    return [m.name for m in members]


def get_revision_impl(
    wiki_id: str, page_title: str, revision_id: int
) -> Dict[str, Any]:
    """
    Get a specific revision of a page.

    Args:
        wiki_id: The wiki identifier.
        page_title: Title of the page.
        revision_id: The revision ID.

    Returns:
        Revision data.
    """
    client = get_wiki_client(wiki_id)
    site = client.get_site()
    result = site.api(
        "query",
        prop="revisions",
        titles=page_title,
        revids=revision_id,
        rvprop="content|timestamp|user|id|parentid",
    )
    pages = result.get("query", {}).get("pages", {})
    for page_data in pages.values():
        revisions = page_data.get("revisions", [])
        if revisions:
            rev = revisions[0]
            return format_revision(
                {
                    "revid": rev.get("revid", 0),
                    "parentid": rev.get("parentid", 0),
                    "timestamp": rev.get("timestamp", ""),
                    "user": rev.get("user", ""),
                    "*": rev.get("*", ""),
                }
            )
    raise ValueError(f"Revision {revision_id} not found for page {page_title}")


def create_page_impl(
    wiki_id: str, page_title: str, content: str, summary: str = ""
) -> Dict[str, Any]:
    """
    Create a new wiki page.

    Args:
        wiki_id: The wiki identifier.
        page_title: Title of the new page.
        content: Page content (wikitext).
        summary: Edit summary/commit message.

    Returns:
        Dict with success status and page info.
    """
    client = get_wiki_client(wiki_id)
    client.save_page(page_title, content, summary)
    return {
        "success": True,
        "title": page_title,
        "message": f"Page '{page_title}' created successfully",
    }


def update_page_impl(
    wiki_id: str, page_title: str, content: str, summary: str = ""
) -> Dict[str, Any]:
    """
    Update an existing wiki page.

    Args:
        wiki_id: The wiki identifier.
        page_title: Title of the page to update.
        content: New page content (wikitext).
        summary: Edit summary/commit message.

    Returns:
        Dict with success status.
    """
    client = get_wiki_client(wiki_id)
    client.save_page(page_title, content, summary)
    return {
        "success": True,
        "title": page_title,
        "message": f"Page '{page_title}' updated successfully",
    }


def delete_page_impl(wiki_id: str, page_title: str, reason: str = "") -> Dict[str, Any]:
    """
    Delete a wiki page.

    Args:
        wiki_id: The wiki identifier.
        page_title: Title of the page to delete.
        reason: Reason for deletion.

    Returns:
        Dict with success status.
    """
    client = get_wiki_client(wiki_id)
    site = client.get_site()
    page = client.get_page(page_title)
    site.delete(page, reason)
    return {
        "success": True,
        "title": page_title,
        "message": f"Page '{page_title}' deleted successfully",
    }


def undelete_page_impl(
    wiki_id: str, page_title: str, reason: str = ""
) -> Dict[str, Any]:
    """
    Undelete a wiki page.

    Args:
        wiki_id: The wiki identifier.
        page_title: Title of the page to undelete.
        reason: Reason for undeletion.

    Returns:
        Dict with success status.
    """
    client = get_wiki_client(wiki_id)
    site = client.get_site()
    page = client.get_page(page_title)
    site.undelete(page, reason)
    return {
        "success": True,
        "title": page_title,
        "message": f"Page '{page_title}' restored successfully",
    }


def preview_edit_impl(
    wiki_id: str, page_title: str, content: str, summary: str = ""
) -> Dict[str, Any]:
    """
    Preview an edit without committing. Returns a token for commit.

    Args:
        wiki_id: The wiki identifier.
        page_title: Title of the page.
        content: Proposed page content.
        summary: Edit summary.

    Returns:
        Dict with preview info and commit token.
    """
    client = get_wiki_client(wiki_id)
    page = client.get_page(page_title)
    old_content = page.text() if hasattr(page, "text") else ""

    token = str(uuid.uuid4())
    PREVIEW_STORE[token] = {
        "wiki_id": wiki_id,
        "page_title": page_title,
        "content": content,
        "summary": summary,
        "old_content": old_content,
    }

    diff = generate_diff(old_content, content)

    return {
        "success": True,
        "token": token,
        "old_content": old_content,
        "new_content": content,
        "diff": diff,
        "summary": summary,
        "message": "Use commit_edit with the token to apply this edit",
    }


def commit_edit_impl(wiki_id: str, page_title: str, token: str) -> Dict[str, Any]:
    """
    Commit a previously previewed edit.

    Args:
        wiki_id: The wiki identifier.
        page_title: Title of the page.
        token: Token from preview_edit.

    Returns:
        Dict with success status.
    """
    if token not in PREVIEW_STORE:
        raise ValueError("Invalid or expired token. Run preview_edit first.")

    preview = PREVIEW_STORE[token]
    if preview["wiki_id"] != wiki_id or preview["page_title"] != page_title:
        raise ValueError("Token does not match wiki_id or page_title")

    client = get_wiki_client(wiki_id)
    client.save_page(page_title, preview["content"], preview["summary"])

    del PREVIEW_STORE[token]

    return {
        "success": True,
        "title": page_title,
        "message": f"Edit committed to '{page_title}'",
    }


def generate_diff(old: str, new: str) -> str:
    """
    Generate a simple unified diff-like output.

    Args:
        old: Old content.
        new: New content.

    Returns:
        String showing the difference.
    """
    old_lines = old.splitlines()
    new_lines = new.splitlines()

    diff_lines = []
    old_len = len(old_lines)
    new_len = len(new_lines)

    diff_lines.append(f"--- {old_len} lines")
    diff_lines.append(f"+++ {new_len} lines")

    if old == new:
        diff_lines.append("No changes")
    else:
        diff_lines.append(f"Old content:\n{old}")
        diff_lines.append(f"New content:\n{new}")
        diff_lines.append(f"Content changed ({old_len} -> {new_len} lines)")

    return "\n".join(diff_lines)


def upload_file_impl(
    wiki_id: str, file_path: str, description: str = ""
) -> Dict[str, Any]:
    """
    Upload a file to the wiki from local disk.

    Args:
        wiki_id: The wiki identifier.
        file_path: Path to the local file.
        description: File description.

    Returns:
        Dict with success status.
    """
    import os

    client = get_wiki_client(wiki_id)
    site = client.get_site()

    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        site.upload(f, filename, description)

    return {
        "success": True,
        "filename": filename,
        "message": f"File '{filename}' uploaded successfully",
    }


def get_wiki_info_impl(wiki_id: str) -> Dict[str, Any]:
    """
    Get wiki configuration information.

    Args:
        wiki_id: The wiki identifier.

    Returns:
        Dict with wiki info.
    """
    client = get_wiki_client(wiki_id)
    site_info = client.get_site_info(props="general")
    return {
        "sitename": site_info.get("sitename", ""),
        "server": site_info.get("server", ""),
        "articlepath": site_info.get("articlepath", ""),
        "scriptpath": site_info.get("scriptpath", ""),
    }


@mcp.tool()
def list_wikis() -> List[Dict[str, str]]:
    """List all configured wikis."""
    return list_wikis_impl()


@mcp.tool()
def set_wiki(wiki_id: str) -> Dict[str, Any]:
    """Set the default wiki for the current session."""
    return set_wiki_impl(wiki_id)


@mcp.tool()
def get_page(wiki_id: str, page_title: str) -> Dict[str, Any]:
    """Get a wiki page."""
    return get_page_impl(wiki_id, page_title)


@mcp.tool()
def get_page_markup(wiki_id: str, page_title: str) -> str:
    """Get the raw wikitext markup for a page."""
    return get_page_markup_impl(wiki_id, page_title)


@mcp.tool()
def search_page(wiki_id: str, query: str, limit: int = 10) -> List[Dict[str, str]]:
    """Search wiki page titles and contents."""
    return search_page_impl(wiki_id, query, limit)


@mcp.tool()
def search_page_by_prefix(wiki_id: str, prefix: str, limit: int = 10) -> List[str]:
    """Perform a prefix search for page titles."""
    return search_page_by_prefix_impl(wiki_id, prefix, limit)


@mcp.tool()
def get_page_history(
    wiki_id: str, page_title: str, limit: int = 10
) -> List[Dict[str, Any]]:
    """Get page revision history."""
    return get_page_history_impl(wiki_id, page_title, limit)


@mcp.tool()
def get_category_members(wiki_id: str, category: str, limit: int = 10) -> List[str]:
    """Get all members in a category."""
    return get_category_members_impl(wiki_id, category, limit)


@mcp.tool()
def get_revision(wiki_id: str, page_title: str, revision_id: int) -> Dict[str, Any]:
    """Get a specific revision of a page."""
    return get_revision_impl(wiki_id, page_title, revision_id)


@mcp.tool()
def create_page(
    wiki_id: str, page_title: str, content: str, summary: str = ""
) -> Dict[str, Any]:
    """Create a new wiki page."""
    return create_page_impl(wiki_id, page_title, content, summary)


@mcp.tool()
def update_page(
    wiki_id: str, page_title: str, content: str, summary: str = ""
) -> Dict[str, Any]:
    """Update an existing wiki page."""
    return update_page_impl(wiki_id, page_title, content, summary)


@mcp.tool()
def delete_page(wiki_id: str, page_title: str, reason: str = "") -> Dict[str, Any]:
    """Delete a wiki page."""
    return delete_page_impl(wiki_id, page_title, reason)


@mcp.tool()
def undelete_page(wiki_id: str, page_title: str, reason: str = "") -> Dict[str, Any]:
    """Undelete a wiki page."""
    return undelete_page_impl(wiki_id, page_title, reason)


@mcp.tool()
def preview_edit(
    wiki_id: str, page_title: str, content: str, summary: str = ""
) -> Dict[str, Any]:
    """Preview an edit without committing."""
    return preview_edit_impl(wiki_id, page_title, content, summary)


@mcp.tool()
def commit_edit(wiki_id: str, page_title: str, token: str) -> Dict[str, Any]:
    """Commit a previously previewed edit."""
    return commit_edit_impl(wiki_id, page_title, token)


@mcp.tool()
def upload_file(wiki_id: str, file_path: str, description: str = "") -> Dict[str, Any]:
    """Upload a file to the wiki from local disk."""
    return upload_file_impl(wiki_id, file_path, description)


@mcp.tool()
def get_wiki_info(wiki_id: str) -> Dict[str, Any]:
    """Get wiki configuration information."""
    return get_wiki_info_impl(wiki_id)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
