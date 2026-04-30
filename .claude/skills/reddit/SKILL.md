---
name: reddit
description: >
  Search and scrape Reddit for community sentiment and unpolished signal.
  Uses public .json endpoints or API.
---

# Reddit Research Skill

## Capabilities
- Search specific subreddits (e.g., r/SaaS, r/ArtificialInteligence).
- Extract comments for sentiment analysis.
- Find real-world reviews and complaints.

## Usage Examples
```bash
# Search for specific terms in a subreddit
reddit search "HeyGen review" --subreddit SaaS --limit 10

# Get comments for a specific post
reddit comments {post_id}
```
