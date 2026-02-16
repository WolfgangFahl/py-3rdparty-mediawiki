# AGENTS.md - Development Guidelines for py-3rdparty-mediawiki

## Project Overview

Python wrapper for mwclient with improvements for 3rd party wikis. Uses the hatch build system.

## Build/Lint/Test Commands

### Installation
```bash
pip install .
# or
scripts/install

# With MCP support (for AI assistants)
scripts/install --mcp
```

### MCP Server
```bash
# Start the MCP server
scripts/mcp

# Or directly
python -m wikibot3rd.mcp_server
```

The MCP server allows AI assistants (Claude, Cursor, ChatGPT) to interact with wikis via the Model Context Protocol. Configure in Claude Desktop:

```json
{
  "mcpServers": {
    "wikibot": {
      "command": "wikibot-mcp"
    }
  }
}
```

### Running Tests

```bash
# Run all tests with unittest discover
python3 -m unittest discover

# Run tests with green (colorful output)
green tests

# Run tests module-by-module
scripts/test --module  # or: python -m unittest tests/test_wikibot.py

# Run a single test class
python -m unittest tests.test_wikibot.TestWikiBot

# Run a single test method
python -m unittest tests.test_wikibot.TestWikiBot.test_encryption
```

### Code Formatting

```bash
# Format and sort imports
scripts/blackisort

# Or individually:
black wikibot3rd tests
isort wikibot3rd tests
```

### Linting
The project uses standard Python tooling. Run `black` and `isort` for formatting compliance.

## Code Style Guidelines

### Imports

- Standard library imports first
- Third-party imports second
- Local project imports last
- Use absolute imports (`from wikibot3rd.xxx import Yyy`)
- Sort imports with `isort`

### Types

- Use type hints for function parameters and return values
- Use `Optional[X]` instead of `X | None` for Python 3.10 compatibility
- Use `typing` module for complex types: `Dict`, `List`, `Any`, etc.

Example:
```python
from typing import Any, Dict, Optional

def method(self, param: str, debug: bool = False) -> Optional[Site]:
    ...
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `WikiBot`, `WikiClient`)
- **Functions/methods**: snake_case (e.g., `get_site()`, `login()`)
- **Variables**: snake_case (e.g., `wiki_user`, `debug`)
- **Constants**: UPPER_SNAKE_CASE
- **Files**: snake_case (e.g., `wikibot.py`, `wiki_client.py`)
- **Tests**: `test_*.py` for test modules, `Test*` for test classes

### Class Structure

- Inherit from `object` explicitly for Python 2 compatibility if needed, otherwise omit
- Use dataclasses for simple data containers (`@dataclass`)
- Use `@property` for computed attributes

```python
@dataclass
class WikiCredentials:
    password: str = field(default=None, repr=False)

    @property
    def has_credentials(self) -> bool:
        ...
```

### Docstrings

Use Google-style docstrings with Args, Returns, Raises sections:

```python
def method(self, wiki_user: WikiUser, debug: bool = False) -> Site:
    """
    Initialize the WikiClient with a WikiUser.

    Args:
        wiki_user: A WikiUser instance containing login credentials.
        debug: A flag to enable debug mode.

    Returns:
        The Site object representing the MediaWiki site.

    Raises:
        ValueError: If the wiki user is invalid.
    """
```

### Error Handling

- Use try/except blocks with specific exception types
- Raise custom exceptions with descriptive messages
- Use `ValueError` for invalid arguments, `RuntimeError` for operational failures

```python
if not self.encrypted:
    raise ValueError("Data is not encrypted")
```

### String Formatting

- Use f-strings for string interpolation
- Use % formatting only for legacy compatibility

```python
msg = f"netloc for family {self.family} is {self.netloc}"
text = "%20s(%10s): %15s %s" % (wu.wikiId, botType, wu.user, wu.url)
```

### Deprecated Methods

When deprecating methods, add a docstring note:

```python
def getSite(self) -> Site:
    """Deprecated: Use get_site instead."""
    return self.get_site()
```

### Deprecation Warnings

Suppress known deprecation warnings when necessary:

```python
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

### Testing Conventions

- Test classes inherit from `BaseWikiTest` (in `tests/`)
- Test methods start with `test_` prefix
- Use `self.assertEqual()`, `self.assertTrue()`, `self.assertIsNone()`, etc.
- Print debugging info with `print()` (can be enabled with debug flags)

```python
class TestWikiBot(BaseWikiTest):
    def test_encryption(self):
        """test encryption/decryption"""
        c = Crypt(cypher, 20, salt)
        secret1 = c.encrypt(expected)
        self.assertEqual(secret, secret1)
```

### File Header

Include standard header:

```python
"""
Created on 2024-01-01

@author: wf
"""
```

### Project Structure

```
wikibot3rd/           # Main package
wikibot3rd_examples/  # Example scripts
tests/                # Test suite
scripts/              # Build/test scripts
docs/                 # Documentation
```

### Dependencies

Key dependencies (see `pyproject.toml`):
- `mwclient` - MediaWiki client
- `pywikibot` - Wikipedia bot framework
- `pybasemkit` - Base utilities
- `pyLodStorage` - Linked data storage
- `requests` - HTTP library
- `pycryptodome` - Cryptography
- `bcrypt` - Password hashing
- `fastmcp` - MCP server (optional, install with `[mcp]`)

### CLI Commands

The project provides CLI entry points:
- `wikibackup`, `wikiedit`, `wikinuke`, `wikipush`, `wikiquery`, `wikiupload`, `wikirestore`, `wikiuser`
- `wikibot-mcp` - MCP server for AI assistants

### Configuration

Wiki user configuration is stored in YAML files.
The default folder for configurations is $HOME/.mediawiki-japi for Legacy compatibility reasons to
a previous java based solution.
Use `WikiUser` class to manage credentials with encryption support.
