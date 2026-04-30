"""Score and rank Instagram reels by engagement and virality."""

from datetime import datetime


def score_reel(reel):
    """Compute performance metrics for a single reel.

    Returns reel dict with added fields:
        virality_ratio   - plays / followers (reach beyond audience)
        engagement_rate  - (likes + comments*3) / plays (depth of engagement)
        save_rate        - saves / plays (bookmark signal)
        recency_boost    - 0-1 boost for recent posts (within 6 months)
        performance      - composite score (0-100)
    """
    plays = reel.get("plays", 0)
    likes = reel.get("likes", 0)
    comments = reel.get("comments", 0)
    saves = reel.get("saves", 0)
    followers = reel.get("followers", 0)

    # Virality: how far beyond existing audience
    virality = plays / followers if followers > 0 else 0

    # Engagement: comments weighted 3x (deeper signal than likes)
    engagement = (likes + comments * 3) / plays if plays > 0 else 0

    # If no play count, fall back to likes-based engagement
    if plays == 0 and followers > 0:
        engagement = (likes + comments * 3) / followers
        virality = likes / followers

    # Save rate: strong signal for share-worthy content
    save_rate = saves / plays if plays > 0 else 0

    # Recency: recent posts get a boost (0-1, linear decay over 6 months)
    recency = 0.5
    timestamp = reel.get("timestamp", "")
    if timestamp:
        try:
            if "T" in str(timestamp):
                pub = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
            else:
                pub = datetime.fromisoformat(str(timestamp))
            days_ago = (datetime.now(pub.tzinfo) - pub).days if pub.tzinfo else (datetime.now() - pub).days
            recency = max(0, 1 - days_ago / 180)
        except (ValueError, TypeError):
            pass

    # Normalize to 0-100 scale
    virality_norm = min(100, virality * 20)       # 5x followers = 100
    engagement_norm = min(100, engagement * 2000)  # 5% = 100
    save_norm = min(100, save_rate * 5000)         # 2% save rate = 100
    recency_norm = recency * 100                   # Direct 0-100

    # Composite: virality matters most, then engagement, saves as bonus
    performance = (
        virality_norm * 0.40
        + engagement_norm * 0.30
        + save_norm * 0.10
        + recency_norm * 0.20
    )

    scored = dict(reel)
    scored["virality_ratio"] = round(virality, 3)
    scored["engagement_rate"] = round(engagement, 4)
    scored["save_rate"] = round(save_rate, 4)
    scored["recency_boost"] = round(recency, 2)
    scored["performance"] = round(performance, 1)
    return scored


def score_and_rank(reels, top_n=15):
    """Score all reels and return top N ranked.

    Filters out:
        - Reels with 0 followers (can't compute virality)
        - Reels with < 100 likes (noise floor)

    Returns sorted list by performance descending with rank added.
    """
    scored = []
    for reel in reels:
        if reel.get("followers", 0) <= 0:
            continue
        if reel.get("likes", 0) < 100 and reel.get("plays", 0) < 1000:
            continue
        scored.append(score_reel(reel))

    scored.sort(
        key=lambda r: (r["performance"], r.get("plays", 0), r.get("likes", 0)),
        reverse=True,
    )

    for i, reel in enumerate(scored[:top_n], 1):
        reel["rank"] = i

    print(f"    {len(scored)} scoreable reels -> top {min(top_n, len(scored))} ranked")
    return scored[:top_n]
