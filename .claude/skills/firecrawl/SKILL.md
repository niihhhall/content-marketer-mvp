---
name: firecrawl
description: >
  Web scraping and crawling using Firecrawl. Use for: deep web searches, 
  scraping JS-heavy sites, extracting structured data from URLs, crawling subdomains.
---

# Firecrawl Skill

## Capabilities
- **Search**: Scour the web for specific queries.
- **Scrape**: Turn any URL into clean Markdown.
- **Crawl**: Follow links to map an entire site.

## Setup
Set `FIRECRAWL_API_KEY` in your environment.

## Usage Examples
```bash
# Search and scrape top 3 results
firecrawl search "AI voice agent pricing" --limit 3

# Scrape a specific URL
firecrawl scrape https://example.com/blog/voice-agents
```
