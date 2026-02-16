# MCP Server Design for py-3rdparty-mediawiki

## What is MCP?

The Model Context Protocol (MCP) is an open standard that enables
AI applications (like Claude Desktop, Cursor, etc.) to connect to
external tools and data sources through a standardized interface.
Instead of hardcoding integrations, MCP defines a protocol where AI
 clients can discover and call server-provided "tools."

## Why Add MCP to This Project?

### Current Problem
Currently, this library provides:
- Python classes (`WikiBot`, `WikiClient`) for programmatic access
- CLI commands (`wikiedit`, `wikiquery`, etc.) for manual use
- No standardized way for AI agents to interact with wikis

### MCP Solution
An MCP server would allow:
- **AI Assistants** (Claude, Cursor, ChatGPT) to directly query and edit wikis
- **Automated workflows** triggered by AI without custom code
- **Natural language interface** to wiki operations
- **Standardized tool discovery** - AI clients automatically see available operations

### Use Cases
1. "Get me the content of page X" → AI calls `get_page` tool
2. "Search for pages containing 'foobar'" → AI calls `search` tool
3. "Update the configuration page with this text" → AI calls `edit_page` tool
4. "List all wikis I have access to" → AI calls `list_wikis` tool
5. "Upload this file to the wiki" → AI calls `upload_file` tool

## Existing Implementations and Related Work

### MediaWiki MCP Server (Professional.Wiki)
The [MediaWiki MCP Server](https://github.com/ProfessionalWiki/MediaWiki-MCP-Server) by Jeroen De Dauw is a production-ready TypeScript implementation (60+ GitHub stars):

**Implementation Details:**
- **Language**: TypeScript (82%)
- **MCP SDK**: Official `@modelcontextprotocol/server`
- **Transport**: STDIO (default) and HTTP support

**Tools Provided:**
| Tool | Description | Auth Required |
|------|-------------|---------------|
| `add-wiki` | Add a new wiki as MCP resource | No |
| `set-wiki` | Set wiki for current session | No |
| `remove-wiki` | Remove a wiki resource | No |
| `get-page` | Get page object | No |
| `get-file` | Get file object | No |
| `get-revision` | Get revision object | No |
| `get-page-history` | Get page revision history | No |
| `search-page` | Search page titles and content | No |
| `search-page-by-prefix` | Prefix search for page titles | No |
| `get-category-members` | Get category members | No |
| `create-page` | Create new page | Yes |
| `update-page` | Update existing page | Yes |
| `delete-page` | Delete page | Yes |
| `undelete-page` | Undelete page | Yes |
| `upload-file` | Upload file from local disk | Yes |
| `upload-file-from-url` | Upload file from URL | Yes |

**Resources:**
- `mcp://wikis/{wikiKey}` - Exposes wiki metadata as readable resources

**Configuration:**
```json
{
  "defaultWiki": "en.wikipedia.org",
  "wikis": {
    "en.wikipedia.org": {
      "server": "https://en.wikipedia.org",
      "articlepath": "/wiki",
      "scriptpath": "/w",
      "token": "oauth2-token",
      "username": null,
      "password": null,
      "private": false
    }
  }
}
```

**Authentication:**
- **Preferred**: OAuth2 access token
- **Fallback**: Bot username/password (from Special:BotPasswords)

**Installation:**
```bash
npx @professional-wiki/mediawiki-mcp-server@latest
```

**Reference**: [GitHub](https://github.com/ProfessionalWiki/MediaWiki-MCP-Server) | [NPM](https://www.npmjs.com/package/@professional-wiki/mediawiki-mcp-server)

### Wiki AI Playgrounds Concept
The [Wiki AI Playgrounds](https://www.semantic-mediawiki.org/wiki/MediaWiki_Users_and_Developers_Conference_Fall_2025/Wiki_AI_Playgrounds) concept (Lightning talk by Wolfgang Fahl at SMWCon Fall 2025) proposes combining:

1. **MCP Server** - Provides AI tool access to wiki operations
2. **MediaWiki Playground** - Preview and testing environment
3. **Approval Workflow** - Human-in-the-loop for write operations

This creates a safer workflow where:
- AI suggests edits (via MCP)
- User previews changes in Playground
- Approved transactions are committed to the wiki

**Key ideas to incorporate:**
- **Preview Mode**: Add a `preview_edit` tool that returns the diff without committing
- **Approval Tokens**: Generate one-time tokens for committing previewed changes
- **Transaction Safety**: Prevent AI from making uncontrolled changes

**Reference**: [Slides](https://docs.google.com/presentation/d/1t5DPM0GYEGBV9WBA2wjkhiPu-tuLCwpxPU4ee9UeCtM/edit) | [Video](https://www.youtube.com/watch?v=wcgvg2rLgPM)

### Related Talks
- **SMWCon 2025**: ["Let AI access your wiki with MCP"](https://www.semantic-mediawiki.org/wiki/MediaWiki_Users_and_Developers_Conference_Fall_2025/Let_AI_access_your_wiki_with_MCP) by Jeroen De Dauw - [Video](https://www.youtube.com/watch?v=vKLt1ezEiWk)
- **SMWCon 2025**: ["Wiki AI Playgrounds"](https://www.semantic-mediawiki.org/wiki/MediaWiki_Users_and_Developers_Conference_Fall_2025/Wiki_AI_Playgrounds) by Wolfgang Fahl - [Video](https://www.youtube.com/watch?v=wcgvg2rLgPM)

### Differentiation Strategy
This project's MCP server should differentiate from existing solutions:

| Feature | MediaWiki MCP Server (Professional.Wiki) | This Project |
|---------|------------------------------------------|---------------|
| Language | TypeScript | Python |
| Multi-wiki | Session-based (add/remove at runtime) | Pre-configured via YAML |
| Credential storage | JSON config file | Existing WikiUser YAML system |
| Password encryption | Plain text in config | Full encrypted credentials (bcrypt/DES) |
| Preview/Approval | Not included | Wiki AI Playgrounds workflow |
| SMW queries | Basic page ops | Full Semantic MediaWiki ask API |
| CLI tools | None | Existing rich CLI (`wikiedit`, etc.) |
| Transport | STDIO, HTTP | STDIO, HTTP |

**Key differentiators for this project:**
1. **Python-based** - Leverages existing py-3rdparty-mediawiki codebase
2. **Encrypted credentials** - Security for production use
3. **SMW integration** - Native Semantic MediaWiki query support
4. **Preview workflow** - Human-in-the-loop for write operations
5. **Pre-configured wikis** - No runtime wiki management needed

## Implementation

### Build Native Python MCP Server
Create a new `wikibot3rd/mcp_server.py` using FastMCP or the official MCP Python SDK:
- Full control over implementation
- Direct access to existing WikiBot/WikiClient classes
- Can add preview/approval workflow

**Compatibility**: Tool names and signatures should match the Professional.Wiki server for easy migration:
- `get-page`, `create-page`, `update-page`, `delete-page`, `undelete-page`
- `search-page`, `search-page-by-prefix`
- `get-page-history`, `get-revision`
- `get-category-members`
- `upload-file`, `upload-file-from-url`
- `add-wiki`, `set-wiki`, `remove-wiki` (optional, for dynamic wiki management)


## Compatibility with MediaWiki MCP Server

To allow users to switch between this Python implementation and the Professional.Wiki
TypeScript implementation, aim for:

### Tool Name Compatibility
Match tool names from the [MediaWiki MCP Server](https://github.com/ProfessionalWiki/MediaWiki-MCP-Server):

| Our Tool | Professional.Wiki Tool | Notes |
|----------|----------------------|-------|
| `get_page` | `get-page` | Different naming convention |
| `create_page` | `create-page` | |
| `update_page` | `update-page` | |
| `delete_page` | `delete-page` | |
| `undelete_page` | `undelete-page` | |
| `search_page` | `search-page` | |
| `search_page_by_prefix` | `search-page-by-prefix` | |
| `get_page_history` | `get-page-history` | |
| `get_revision` | `get-revision` | |
| `get_category_members` | `get-category-members` | |
| `upload_file` | `upload-file` | |
| `upload_file_from_url` | `upload-file-from-url` | |

### Configuration Compatibility
- Support both our YAML format and their JSON config format
- Map `token`/`username`/`password` fields identically

### Resource Compatibility
- Support `mcp://wikis/{wikiKey}` resource URI format

This allows users to:
1. Use existing Claude Desktop/Cursor configurations
2. Migrate between implementations without client changes
3. Use documentation from the larger MediaWiki MCP community

## What Will the MCP Server Do?

The server exposes wiki operations as **tools** that AI clients can call:

### Read Operations
| Tool | Description | Parameters |
|------|-------------|------------|
| `list_wikis` | List configured wikis | `filter_pattern` (optional) |
| `get_page` | Get page content | `wiki_id`, `page_title` |
| `search` | Search wiki pages | `wiki_id`, `query`, `limit` |
| `get_page_info` | Get page metadata | `wiki_id`, `page_title` |
| `list_categories` | List wiki categories | `wiki_id` |

### Write Operations
| Tool | Description | Parameters |
|------|-------------|------------|
| `preview_edit` | Preview edit without committing | `wiki_id`, `page_title`, `content`, `summary` |
| `edit_page` | Edit/create a page (commits immediately) | `wiki_id`, `page_title`, `content`, `summary` |
| `commit_edit` | Commit a previewed edit using token | `wiki_id`, `page_title`, `token` |
| `upload_file` | Upload a file | `wiki_id`, `file_path`, `description` |
| `delete_page` | Delete a page | `wiki_id`, `page_title`, `reason` |

### Admin Operations
| Tool | Description | Parameters |
|------|-------------|------------|
| `list_users` | List wiki users | `wiki_id` |
| `get_wiki_info` | Get wiki configuration | `wiki_id` |

## Interface Design

### Tool Signatures (Python)

```python
@mcp.tool()
def list_wikis(filter_pattern: Optional[str] = None) -> List[Dict[str, str]]:
    """
    List configured wikis the bot can access.

    Args:
        filter_pattern: Optional regex to filter wiki URLs/names

    Returns:
        List of dicts with wikiId, url, user
    """

@mcp.tool()
def get_page(wiki_id: str, page_title: str) -> str:
    """
    Get the content of a wiki page.

    Args:
        wiki_id: The wiki identifier (e.g., 'semantic-mediawiki.org')
        page_title: Title of the page to retrieve

    Returns:
        Page content as wikitext string
    """

@mcp.tool()
def edit_page(wiki_id: str, page_title: str, content: str,
              summary: str = "") -> Dict[str, Any]:
    """
    Edit or create a wiki page.

    Args:
        wiki_id: The wiki identifier
        page_title: Title of the page
        content: New page content (wikitext)
        summary: Edit summary/commit message

    Returns:
        Dict with success status and revision info
    """

@mcp.tool()
def search(wiki_id: str, query: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Search for pages on a wiki.

    Args:
        wiki_id: The wiki identifier
        query: Search query
        limit: Maximum results (default 10)

    Returns:
        List of matching pages with title and snippet
    """
```

### Return Format

All tools return structured data (JSON-serializable), not raw objects:

```python
# Success
{"success": True, "data": {...}}

# Error
{"success": False, "error": "Page not found", "error_code": "missing"}
```

## Authorization

### Authentication Model
The MCP server uses the existing `WikiUser` credential system:

1. **Credential Loading**: Reads from YAML config files in `~/.mediawiki-japi/`
2. **Per-Wiki Authentication**: Each wiki can have different credentials
3. **Encryption Support**: Passwords can be stored encrypted (via `WikiCredentials`)

### Authorization Levels

| Level | Access | Tools Allowed |
|-------|--------|---------------|
| `read` | Public wikis | `list_wikis`, `get_page`, `search`, `get_page_info`, `list_categories` |
| `write` | Read-write wikis | All read tools + `edit_page`, `upload_file`, `delete_page` |
| `admin` | Admin access | All tools + `list_users`, `get_wiki_info` |

### Implementation Options

#### Option 1: Per-Tool Authorization (Recommended)
```python
@mcp.tool()
def edit_page(wiki_id: str, ...):
    wiki_user = WikiUser.ofWikiId(wiki_id)
    if not wiki_user.has_write_access:
        raise PermissionError(f"No write access to {wiki_id}")
    ...
```

#### Option 2: Capability-Based
```python
# In WikiUser config:
wiki_users:
  mywiki:
    url: https://example.org
    capabilities: [read, write]  # or [read only]
```

#### Option 3: Token-Based (Future)
```python
# MCP server accepts API token
@mcp.tool()
def edit_page(wiki_id: str, api_token: str, ...):
    if not validate_token(api_token, wiki_id, "write"):
        raise PermissionError("Invalid token")
```

### Security Considerations

1. **No credential storage in MCP config**: Credentials stay in existing YAML files
2. **Audit logging**: Log all tool calls with user/wiki/timestamp
3. **Rate limiting**: Prevent abuse of write operations
4. **Connection pooling**: Reuse mwclient connections efficiently

## Deployment

### Local (STDIO)
For development and local AI tools:
```bash
python -m wikibot3rd.mcp_server
```

### Configuration (Claude Desktop example)
```json
{
  "mcpServers": {
    "wikibot": {
      "command": "python",
      "args": ["-m", "wikibot3rd.mcp_server"],
      "env": {
        "WIKIBOT_CONFIG_DIR": "~/.mediawiki-japi"
      }
    }
  }
}
```

## Future Enhancements

- **Preview Mode**: Tools to preview edits before committing (inspired by Wiki AI Playgrounds)
- **Approval Tokens**: One-time tokens for committing previewed changes
- **Prompts**: Pre-defined prompts for common tasks ("Summarize this page", "Find related pages")
- **Resources**: Expose wiki configs, user lists as readable resources
- **Multi-wiki atomic operations**: Transaction support across wikis
- **Webhooks**: Notify external systems of wiki changes
- **SMW Queries**: Direct Semantic MediaWiki `ask` API integration
