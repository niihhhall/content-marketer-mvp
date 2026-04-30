"""Analyze Instagram reel captions for hooks, themes, and content patterns."""

import re
from collections import Counter


# Theme categories by keyword signals in captions.
# Customize these to match your niche.
THEME_KEYWORDS = {
    "AI Tools / Automation": [
        "ai", "artificial intelligence", "automate", "automation", "chatgpt",
        "claude", "claude code", "gpt", "openai", "gemini", "copilot",
        "agent", "workflow", "no-code", "low-code", "cursor", "vibe cod",
    ],
    "Marketing / Growth": [
        "marketing", "growth", "leads", "funnel", "ads", "campaign",
        "content strategy", "social media", "engagement", "audience",
        "instagram", "tiktok", "reach", "viral", "algorithm",
    ],
    "Sales / Revenue": [
        "sales", "revenue", "client", "close", "deal", "dm",
        "outreach", "prospect", "cold", "pitch", "booking",
        "high ticket", "convert", "commission",
    ],
    "Entrepreneurship": [
        "entrepreneur", "business", "startup", "agency", "freelanc",
        "founder", "side hustle", "scale", "bootstrap", "solopreneur",
    ],
    "Productivity / Systems": [
        "productiv", "system", "workflow", "notion", "template",
        "organize", "efficiency", "routine", "hack", "shortcut",
        "time management", "sop",
    ],
    "Tutorial / How-To": [
        "how to", "step by step", "tutorial", "guide", "learn",
        "beginner", "walkthrough", "setup", "install", "config",
    ],
    "Finance / Money": [
        "money", "income", "passive", "investing", "wealth",
        "profit", "earn", "cash", "financial", "bank",
    ],
    "Design / Creative": [
        "design", "canva", "photoshop", "figma", "creative",
        "brand", "aesthetic", "visual", "font", "color",
    ],
    "Personal Development": [
        "mindset", "discipline", "habit", "motivation", "success",
        "confidence", "focus", "stoic", "grind",
    ],
}

# Caption hook patterns (first line/sentence patterns)
HOOK_PATTERNS = {
    "Tool Reveal": [
        r"this (?:ai )?tool", r"I found", r"just discovered",
        r"new tool", r"(?:game|life) chang", r"you need this",
    ],
    "Result / Proof": [
        r"\d+[kKmM]?\+?\s*(?:followers|views|leads|clients|sales|revenue)",
        r"(?:made|earned|generated)\s*\$?\d+",
        r"results", r"proof", r"it works",
    ],
    "Contrarian / Myth-Bust": [
        r"stop", r"don'?t", r"you'?re (?:doing it )?wrong",
        r"nobody (?:tells|talks)", r"myth", r"overrated",
        r"unpopular opinion", r"hot take",
    ],
    "How-To / Tutorial": [
        r"how (?:to|I)", r"step[- ]by[- ]step", r"here'?s how",
        r"do this", r"try this", r"the (?:exact|simple) way",
    ],
    "Listicle / Number": [
        r"^\d+\s+", r"\d+\s+(?:ways|tips|tools|apps|things|reasons|hacks)",
        r"top\s+\d+",
    ],
    "Question / Curiosity": [
        r"^(?:did you|have you|do you|why do|what if|ever wonder)",
        r"\?$", r"guess what",
    ],
    "Speed / Shortcut": [
        r"in \d+ (?:seconds?|minutes?|mins?)",
        r"(?:instant|quick|fast|rapid)", r"one click",
        r"in seconds", r"shortcut",
    ],
    "Before / After": [
        r"before.*after", r"vs\.?", r"compared to",
        r"old way.*new way", r"then.*now",
    ],
}


def _extract_hook(caption):
    """Extract the hook (first meaningful line) from a caption."""
    if not caption:
        return ""
    lines = caption.strip().split("\n")
    hook = lines[0].strip()
    if len(hook) < 15 and len(lines) > 1:
        hook = f"{hook} {lines[1].strip()}"
    return hook[:200]


def classify_theme(caption):
    """Classify reel theme from caption keywords."""
    text = caption.lower()
    scores = {}
    for theme, keywords in THEME_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[theme] = score

    if not scores:
        return "Uncategorized"

    return max(scores, key=scores.get)


def detect_hook_pattern(caption):
    """Detect the hook pattern used in the caption opening."""
    if not caption:
        return "General"

    hook = _extract_hook(caption).lower()
    for pattern_name, patterns in HOOK_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, hook):
                return pattern_name

    return "General"


def detect_content_format(reel):
    """Infer content format from available metadata."""
    caption = (reel.get("caption") or "").lower()

    if any(kw in caption for kw in ["screen record", "tutorial", "walkthrough", "step by step"]):
        return "Screen Recording"
    if any(kw in caption for kw in ["talking head", "face cam"]):
        return "Talking Head"
    if any(kw in caption for kw in ["carousel", "slide"]):
        return "Carousel-Style"
    if any(kw in caption for kw in ["voiceover", "voice over", "narrat"]):
        return "Voiceover + B-roll"

    return "Unknown"


def analyze_reel(reel):
    """Full analysis of a single reel. Returns reel dict with analysis fields added."""
    caption = reel.get("caption", "")

    analyzed = dict(reel)
    analyzed["hook"] = _extract_hook(caption)
    analyzed["theme"] = classify_theme(caption)
    analyzed["hook_pattern"] = detect_hook_pattern(caption)
    analyzed["content_format"] = detect_content_format(reel)
    analyzed["caption_length"] = len(caption)
    analyzed["has_cta"] = bool(re.search(
        r"(?:follow|save|share|comment|link in bio|dm me|tap|click|swipe)",
        caption.lower(),
    ))
    analyzed["has_emoji"] = bool(re.search(r"[\U0001f300-\U0001f9ff]", caption))
    analyzed["hashtag_count"] = len(re.findall(r"#\w+", caption))
    return analyzed


def analyze_all(ranked_reels):
    """Analyze all ranked reels."""
    return [analyze_reel(r) for r in ranked_reels]


def compute_insights(analyzed_reels):
    """Compute aggregate insights across all analyzed reels.

    Returns dict with:
        top_themes, top_hook_patterns, top_formats,
        avg_caption_length, cta_pct, avg_hashtags,
        theme_avg_performance
    """
    themes = Counter()
    patterns = Counter()
    formats = Counter()
    theme_perf = {}

    for reel in analyzed_reels:
        theme = reel.get("theme", "Uncategorized")
        themes[theme] += 1
        patterns[reel.get("hook_pattern", "General")] += 1
        formats[reel.get("content_format", "Unknown")] += 1

        if theme not in theme_perf:
            theme_perf[theme] = []
        theme_perf[theme].append(reel.get("performance", 0))

    theme_avg = {
        theme: round(sum(scores) / len(scores), 1)
        for theme, scores in theme_perf.items()
    }

    total_caption_len = sum(r.get("caption_length", 0) for r in analyzed_reels)
    avg_caption = round(total_caption_len / len(analyzed_reels), 0) if analyzed_reels else 0

    num_with_cta = sum(1 for r in analyzed_reels if r.get("has_cta"))
    total_hashtags = sum(r.get("hashtag_count", 0) for r in analyzed_reels)
    avg_hashtags = round(total_hashtags / len(analyzed_reels), 1) if analyzed_reels else 0

    return {
        "top_themes": themes.most_common(10),
        "top_hook_patterns": patterns.most_common(10),
        "top_formats": formats.most_common(10),
        "avg_caption_length": avg_caption,
        "cta_pct": round(num_with_cta / len(analyzed_reels) * 100, 1) if analyzed_reels else 0,
        "avg_hashtags": avg_hashtags,
        "theme_avg_performance": theme_avg,
    }
