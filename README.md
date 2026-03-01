# parallel-mcp

A web intelligence MCP server powered by [Parallel AI](https://parallel.ai). Provides real-time web search, content extraction, and grounded Q&A — including the ability to scrape X/Twitter profiles that the X API itself can't access without elevated pricing plans.

## Features

- **Web-grounded chat** — Ask questions, get answers with citations from live web data
- **Web search** — Objective-driven search with relevant excerpts
- **URL extraction** — Scrape any public URL into structured markdown (including X/Twitter)
- **3 tools** covering search, extract, and chat

## Setup

1. Get a Parallel AI API key from [parallel.ai](https://parallel.ai)
2. Configure the key in your Dedalus MCP client

## Available Tools

### Chat

- `parallel_ask` — Ask a web-grounded question. Models: `speed`, `lite`, `base`, `core`

### Search

- `parallel_search` — Search the web with an objective and specific queries

### Extract

- `parallel_extract` — Extract structured content from URLs (works on X/Twitter, LinkedIn, etc.)

## Example Queries

```console
parallel_ask("How many followers does @WindsorNguyen have on X?")

parallel_search(
    objective="Find Dedalus Labs funding info",
    search_queries=["Dedalus Labs YC S25 funding", "dedaluslabs.ai"],
)

parallel_extract(
    urls=["https://x.com/WindsorNguyen"],
    objective="Extract follower count and bio",
)
```

## Running

```bash
cd parallel-mcp
uv run python src/main.py
```

## License

MIT
