"""Scrape Instagram competitor reels via DataPrism REST API (Apify fallback)."""

import json
import os
import time
from datetime import datetime

import requests

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
COMPETITORS_PATH = os.path.join(SCRIPT_DIR, "competitors.json")

DATAPRISM_BASE = "https://platform.dataprism.dev/api/v1"
DATAPRISM_KEY = os.environ.get("DATAPRISM_API_KEY", "")

APIFY_BASE = "https://api.apify.com/v2"
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
APIFY_IG_ACTOR = "apify~instagram-scraper"


def _dataprism_request(endpoint, data, timeout=120):
    """Make an authenticated DataPrism API request."""
    url = f"{DATAPRISM_BASE}{endpoint}"
    headers = {
        "X-API-KEY": DATAPRISM_KEY,
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, json=data, timeout=timeout)
    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"DataPrism request failed: {resp.status_code} {resp.text[:200]}"
        )
    return json.loads(resp.text, strict=False)


def load_competitors():
    """Load the local competitors list."""
    if not os.path.exists(COMPETITORS_PATH):
        return []
    with open(COMPETITORS_PATH) as f:
        data = json.load(f)
    return data.get("competitors", [])


def save_competitors(competitors):
    """Save updated competitors list."""
    with open(COMPETITORS_PATH, "w") as f:
        json.dump({"competitors": competitors}, f, indent=2)
        f.write("\n")


def add_competitor(username, followers, notes=""):
    """Add or update a competitor."""
    competitors = load_competitors()
    username = username.lstrip("@").strip()

    existing = [c for c in competitors if c["username"] == username]
    if existing:
        existing[0]["followers"] = followers
        if notes:
            existing[0]["notes"] = notes
        print(f"Updated @{username} (followers: {followers})")
    else:
        entry = {"username": username, "followers": followers}
        if notes:
            entry["notes"] = notes
        competitors.append(entry)
        print(f"Added @{username} (followers: {followers})")

    save_competitors(competitors)


def remove_competitor(username):
    """Remove a competitor by username."""
    competitors = load_competitors()
    username = username.lstrip("@").strip()
    before = len(competitors)
    competitors = [c for c in competitors if c["username"] != username]
    if len(competitors) < before:
        save_competitors(competitors)
        print(f"Removed @{username}")
    else:
        print(f"@{username} not found in competitor list")


def normalize_reel(raw, username, followers=0):
    """Normalize a raw post/reel from any API into a standard dict.

    This handles multiple response formats. If you swap in a different
    scraping API, you may need to adjust the field names here.
    """
    media_list = raw.get("media", [])
    is_video = any(m.get("type") == "video" for m in media_list) if media_list else raw.get("type") == "video"

    likes = raw.get("likesCount") or raw.get("like_count") or raw.get("likes", 0)
    comments = raw.get("commentsCount") or raw.get("comment_count") or raw.get("comments", 0)
    plays = raw.get("videoPlayCount") or raw.get("play_count") or raw.get("plays") or raw.get("videoViewCount", 0)
    saves = raw.get("savesCount") or raw.get("save_count") or raw.get("saves", 0)

    caption = raw.get("caption") or raw.get("text") or ""
    if isinstance(caption, dict):
        caption = caption.get("text", "")

    timestamp = raw.get("timestamp") or raw.get("taken_at") or raw.get("date") or ""
    if isinstance(timestamp, (int, float)):
        try:
            timestamp = datetime.fromtimestamp(timestamp).isoformat()
        except (OSError, ValueError):
            timestamp = ""

    url = raw.get("url") or raw.get("shortCode", "")
    if url and not url.startswith("http"):
        url = f"https://www.instagram.com/reel/{url}/"

    thumbnail = ""
    if media_list:
        thumbnail = media_list[0].get("url", "")
    if not thumbnail:
        thumbnail = raw.get("displayUrl") or raw.get("thumbnail_url", "")

    return {
        "username": username,
        "followers": followers,
        "caption": caption[:500],
        "likes": int(likes) if likes else 0,
        "comments": int(comments) if comments else 0,
        "plays": int(plays) if plays else 0,
        "saves": int(saves) if saves else 0,
        "is_video": is_video,
        "url": url,
        "thumbnail_url": thumbnail,
        "timestamp": str(timestamp),
    }


def scrape_competitor_reels_dataprism(username, max_reels=30, cache=None):
    """Scrape reels from a single competitor via DataPrism."""
    if not DATAPRISM_KEY:
        raise ValueError("No DataPrism API key. Set DATAPRISM_API_KEY env var.")

    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"ig:{username}:{max_reels}:{today}"
    if cache:
        cached = cache.get(cache_key)
        if cached:
            print(f"    (cached {len(cached)} reels for @{username})")
            return cached

    print(f"    Scraping @{username} via DataPrism ({max_reels} posts)...")
    resp = _dataprism_request("/tools/instagram/scrape", {
        "username": username,
        "posts": max_reels,
    }, timeout=120)

    data = resp.get("data", resp)
    profile = data.get("profile", {})
    followers = profile.get("followers", 0)
    posts = data.get("posts", [])

    reels = []
    for post in posts:
        reel = normalize_reel(post, username, followers)
        reels.append(reel)

    print(f"    Got {len(reels)} posts for @{username} ({followers} followers)")

    if cache and reels:
        cache.set(cache_key, reels)

    return reels


def scrape_competitor_reels_apify(username, max_reels=30, cache=None):
    """Fallback: scrape reels via Apify instagram-scraper."""
    if not APIFY_TOKEN:
        raise ValueError("No Apify token. Set APIFY_TOKEN env var.")

    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"ig-apify:{username}:{max_reels}:{today}"
    if cache:
        cached = cache.get(cache_key)
        if cached:
            print(f"    (cached {len(cached)} reels for @{username} via Apify)")
            return cached

    print(f"    Scraping @{username} via Apify ({max_reels} reels)...")
    run_url = f"{APIFY_BASE}/acts/{APIFY_IG_ACTOR}/run-sync-get-dataset-items"
    params = {"token": APIFY_TOKEN}
    payload = {
        "directUrls": [f"https://www.instagram.com/{username}/"],
        "resultsType": "posts",
        "resultsLimit": max_reels,
    }
    resp = requests.post(run_url, params=params, json=payload, timeout=300)
    if resp.status_code != 201:
        raise RuntimeError(f"Apify error: {resp.status_code} {resp.text[:200]}")

    items = resp.json()
    reels = []
    for item in items:
        reel = normalize_reel(item, username, item.get("ownerFollowerCount", 0))
        reels.append(reel)

    print(f"    Got {len(reels)} posts for @{username} via Apify")

    if cache and reels:
        cache.set(cache_key, reels)

    return reels


def scrape_all_competitors(max_reels_per=30, cache=None, use_apify_fallback=True):
    """Scrape reels from all competitors in competitors.json.

    Tries DataPrism first, falls back to Apify if configured.
    Returns combined list of normalized reel dicts.
    """
    competitors = load_competitors()
    all_reels = []

    for comp in competitors:
        username = comp["username"]
        try:
            reels = scrape_competitor_reels_dataprism(
                username, max_reels=max_reels_per, cache=cache
            )
            if comp.get("followers"):
                for r in reels:
                    if not r["followers"]:
                        r["followers"] = comp["followers"]
            all_reels.extend(reels)
        except Exception as e:
            print(f"    DataPrism failed for @{username}: {e}")
            if use_apify_fallback and APIFY_TOKEN:
                try:
                    reels = scrape_competitor_reels_apify(
                        username, max_reels=max_reels_per, cache=cache
                    )
                    if comp.get("followers"):
                        for r in reels:
                            if not r["followers"]:
                                r["followers"] = comp["followers"]
                    all_reels.extend(reels)
                except Exception as e2:
                    print(f"    Apify fallback also failed for @{username}: {e2}")
            else:
                print(f"    Skipping @{username} (no Apify fallback)")

        time.sleep(1)

    print(f"    Total: {len(all_reels)} reels from {len(competitors)} competitors")
    return all_reels
