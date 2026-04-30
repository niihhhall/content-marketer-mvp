---
name: x-search
description: >
  Search X (Twitter) for real-time discourse and thought leader insights.
---

# X Search Skill

## Capabilities
- Real-time search for trends and breaking news.
- Monitor specific thought leaders.
- Identify community discourse patterns.

## Setup
Set `XAI_API_KEY` (Grok) or `X_API_TOKEN` in your environment.

## Usage Examples
```bash
# Search for recent posts
x-search "Claude Code deep research" --limit 20

# Search from a specific user
x-search "from:anthropic AI agents"
```
