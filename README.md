# Intelligent Navigator

An LLM-guided web exploration agent that automatically discovers and maps the full navigation structure of a web application. It uses a three-agent architecture to systematically explore pages, handle authentication, and build a complete navigation graph.

## How It Works

The system uses three specialized agents that collaborate:

1. **Orchestrator** -- strategic planner that decides which page to visit next, manages the exploration queue, and coordinates login/logout for role-based exploration
2. **Navigator** -- tactical executor that reads the current page's DOM and clicks the right elements to reach a target page
3. **Explorer** -- thorough page analyzer that scrolls through the page, extracts all visible links, and discovers hidden content behind tabs, modals, dropdowns, and collapsible sections

The agents communicate through structured commands and results, with the Orchestrator driving the overall exploration loop.

## Architecture

```
intelligent_navigator/
├── __init__.py                 # Exports: Orchestrator, ExplorationResult
├── __main__.py                 # CLI entry point
├── visualize.py                # Graph visualization (networkx + matplotlib)
├── agents/                     # The three-agent system
│   ├── orchestrator.py         # Strategic: which page to visit next
│   ├── navigator.py            # Tactical: how to reach a target page
│   ├── explorer.py             # Thorough: extract all links from a page
│   ├── sub_state.py            # Sub-state discovery (tabs, modals, etc.)
│   └── prompts.py              # All LLM prompt templates
├── browser/                    # Browser automation (Playwright)
│   ├── session.py              # Browser session management
│   ├── controller.py           # Command execution (click, type, scroll)
│   ├── dom_builder.py          # JavaScript DOM extraction
│   ├── dom_parser.py           # DOM tree parsing and element mapping
│   └── dom_helper.py           # Full-page DOM capture with scrolling
├── core/                       # Shared foundation
│   ├── llm.py                  # OpenAI API client wrapper
│   ├── models.py               # All data models (dataclasses)
│   ├── utils.py                # Shared utilities (JSON parsing, logging)
│   └── logging.py              # Debug file management
└── exploration/                # Exploration algorithms and state
    ├── graph.py                # Navigation graph (directed graph of pages)
    ├── page_identity.py        # URL normalization and page deduplication
    ├── link_extractor.py       # DOM-based link extraction
    ├── queue.py                # Exploration frontier queue
    ├── loop_detector.py        # Cycle detection and prevention
    └── credentials.py          # Credential parsing for multi-role exploration
```

## Installation

```bash
# Install the package
pip install -e .

# Install Playwright browsers
playwright install chromium
```

## Usage

### CLI

```bash
python -m intelligent_navigator \
    --url http://localhost:3000 \
    --credentials path/to/credentials.md \
    --navigation path/to/Navigation.md \
    --output output/ \
    --api-key "sk-..." \
    --max-steps 100 \
    --max-pages 50 \
    --debug
```

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--url` | (required) | Base URL of the web application |
| `--credentials` | `""` | Path to credentials file (markdown with username/password/role) |
| `--functional-desc` | `""` | Path to functional description text file |
| `--navigation` | `""` | Path to Navigation.md (expected pages checklist) |
| `--output` | `output` | Output directory for navigation graph JSON |
| `--api-key` | `$OPENAI_API_KEY` | OpenAI API key |
| `--model` | `gpt-4o-mini` | LLM model to use |
| `--max-steps` | `100` | Maximum exploration steps |
| `--max-pages` | `50` | Maximum pages to visit |
| `--max-llm-calls` | `300` | Maximum total LLM calls across all agents |
| `--debug` | `false` | Enable debug logging to file |

### Programmatic API

```python
from intelligent_navigator import Orchestrator

config = {
    "base_url": "http://localhost:3000",
    "api_key": "sk-...",
    "credentials_file": "credentials.md",
    "navigation_file": "Navigation.md",
    "output_dir": "output",
    "max_steps": 100,
    "max_pages": 50,
    "debug": True,
}

orchestrator = Orchestrator(config)
result = orchestrator.run()

# result.navigation_graph contains the full graph
# result.exploration_stats contains LLM call counts, coverage, etc.
```

### Visualizing the Graph

```bash
# Interactive display
python -m intelligent_navigator.visualize output/navigation_graph.json

# Save to file
python -m intelligent_navigator.visualize output/navigation_graph.json graph.png

# Headless (no display, auto-save)
python -m intelligent_navigator.visualize output/navigation_graph.json --no-show
```

Requires `networkx` and `matplotlib` (`pip install networkx matplotlib`).

## Input Files

### Credentials File

A markdown file listing user accounts with roles:

```markdown
## Accounts

| Username | Password | Role |
|----------|----------|------|
| admin@example.com | Admin123! | Admin |
| user@example.com | User123! | Student |
```

### Navigation File

A markdown checklist of expected pages (used by the Orchestrator to ensure completeness):

```markdown
## Public Pages
- [ ] Home (/)
- [ ] Login (/login)

## Admin Pages
- [ ] Dashboard (/admin/dashboard)
- [ ] User Management (/admin/users)
```

## Output

The main output is `navigation_graph.json` containing:

- **Navigation graph**: nodes (pages) and edges (navigation paths) with role annotations
- **Exploration stats**: LLM call breakdown, steps taken, queue stats, coverage summary
- **Role information**: which roles were explored and what pages each role can access

## Example Project

See `examples/parabank/` for a sample web application configuration with credentials, functional specification, and expected navigation structure.
