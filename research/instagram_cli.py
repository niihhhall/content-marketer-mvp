#!/usr/bin/env python3
"""
Instagram Competitor Research CLI - find top-performing reels and extract content patterns.

Usage:
    python3 instagram_cli.py research                          # Full pipeline
    python3 instagram_cli.py research --reels-per 50 --top 20  # Custom limits
    python3 instagram_cli.py research --dry-run                # Preview only

    python3 instagram_cli.py competitors --list
    python3 instagram_cli.py competitors --add some_creator --followers 500000 --notes "AI tools"
    python3 instagram_cli.py competitors --remove some_creator

    python3 instagram_cli.py report --latest
    python3 instagram_cli.py report --date 2026-03-19
    python3 instagram_cli.py report --format json

    python3 instagram_cli.py cache --stats
    python3 instagram_cli.py cache --clear
"""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def cmd_research(args):
    """Run Instagram competitor research pipeline."""
    from cache.store import CacheStore
    from instagram.scraper import load_competitors
    from pipeline.instagram_research import create_instagram_research_pipeline

    competitors = load_competitors()
    reels_per = args.reels_per
    top_n = args.top

    print(f"\n{'='*60}")
    print(f"  Instagram Competitor Research")
    comp_names = ", ".join(f"@{c['username']}" for c in competitors)
    print(f"  Competitors: {comp_names}")
    print(f"  Reels per competitor: {reels_per} | Top: {top_n}")
    print(f"{'='*60}\n")

    if args.dry_run:
        cost_est = len(competitors) * reels_per * 0.001
        print("DRY RUN - would scrape:")
        for c in competitors:
            print(f"  @{c['username']} ({c.get('followers', '?')} followers) - {reels_per} reels")
        print(f"\nEstimated cost: ~${cost_est:.2f}")
        print(f"Total reels to fetch: {len(competitors) * reels_per}")
        return

    cache = CacheStore() if not args.no_cache else None
    pipeline = create_instagram_research_pipeline()

    context = {
        "reels_per_competitor": reels_per,
        "top_n": top_n,
        "cache": cache,
    }

    result = pipeline.run(context)

    print(f"\n{'='*60}")
    print(f"  Research complete!")
    print(f"  Report: {result.get('report_md_path', 'N/A')}")
    print(f"{'='*60}\n")

    analyzed = result.get("analyzed_reels", [])
    if analyzed:
        print(f"Top {len(analyzed)} reels:\n")
        for reel in analyzed:
            plays = reel.get("plays", 0)
            p_str = f"{plays/1_000_000:.1f}M" if plays >= 1_000_000 else f"{plays/1000:.1f}K" if plays >= 1000 else str(plays)
            likes = reel.get("likes", 0)
            l_str = f"{likes/1_000_000:.1f}M" if likes >= 1_000_000 else f"{likes/1000:.1f}K" if likes >= 1000 else str(likes)

            print(
                f"  {reel['rank']:2d}. [@{reel.get('username', '?')}] "
                f"{reel.get('theme', '?')}"
            )
            print(
                f"      {p_str} plays | {l_str} likes | "
                f"{reel['virality_ratio']:.2f}x viral | "
                f"{reel.get('hook_pattern', '?')}"
            )
            hook = reel.get("hook", "")
            if hook:
                print(f"      \"{hook[:80]}{'...' if len(hook) > 80 else ''}\"")
            print()


def cmd_competitors(args):
    """Manage competitor list."""
    from instagram.scraper import load_competitors, add_competitor, remove_competitor

    if args.list:
        competitors = load_competitors()
        if not competitors:
            print("No competitors tracked. Use --add to add one.")
            return
        print(f"Tracked competitors ({len(competitors)}):\n")
        for c in competitors:
            notes = c.get("notes", "")
            print(f"  @{c['username']} ({c.get('followers', '?')} followers)")
            if notes:
                print(f"    Notes: {notes}")
        return

    if args.add:
        if not args.followers:
            print("ERROR: --followers required with --add")
            return
        add_competitor(args.add, args.followers, args.notes or "")
        return

    if args.remove:
        remove_competitor(args.remove)
        return

    print("Use --list, --add, or --remove")


def cmd_report(args):
    """View Instagram research reports."""
    from output.reporter import find_ig_report

    md_path, json_path = find_ig_report(date=args.date)

    if not md_path:
        print("No report found. Run 'instagram_cli.py research' first.")
        return

    if args.format == "json" and json_path:
        with open(json_path) as f:
            data = json.load(f)
        print(json.dumps(data, indent=2))
    elif args.format == "markdown":
        with open(md_path) as f:
            print(f.read())
    else:
        with open(md_path) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.startswith("## Detailed"):
                break
            print(line)


def cmd_cache(args):
    """Manage the fetch cache."""
    from cache.store import CacheStore

    cache = CacheStore()
    if args.clear:
        cache.clear()
        print("Cache cleared.")
    elif args.stats:
        stats = cache.stats()
        print(f"Cache statistics:")
        print(f"  Total entries:  {stats['total_entries']}")
        print(f"  Active:         {stats['active_entries']}")
        print(f"  Expired:        {stats['expired_entries']}")
        print(f"  Size on disk:   {stats['size_kb']} KB")
        print(f"  TTL:            {stats['ttl_hours']} hours")
    else:
        print("Use --clear or --stats")


def main():
    parser = argparse.ArgumentParser(
        description="Instagram Competitor Research - find top reels and extract content patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command")

    # research
    p_res = sub.add_parser("research", help="Run competitor research pipeline")
    p_res.add_argument(
        "--reels-per", type=int, default=30,
        help="Reels to scrape per competitor (default: 30)"
    )
    p_res.add_argument(
        "--top", type=int, default=15,
        help="Number of top reels in report (default: 15)"
    )
    p_res.add_argument(
        "--dry-run", action="store_true",
        help="Preview what would be scraped without API calls"
    )
    p_res.add_argument(
        "--no-cache", action="store_true",
        help="Bypass cache (force fresh scrape)"
    )
    p_res.set_defaults(func=cmd_research)

    # competitors
    p_comp = sub.add_parser("competitors", help="Manage tracked competitors")
    p_comp.add_argument("--list", action="store_true", help="List all competitors")
    p_comp.add_argument("--add", help="Add a competitor (username)")
    p_comp.add_argument("--remove", help="Remove a competitor (username)")
    p_comp.add_argument("--followers", type=int, help="Follower count (used with --add)")
    p_comp.add_argument("--notes", help="Notes about the competitor (used with --add)")
    p_comp.set_defaults(func=cmd_competitors)

    # report
    p_rep = sub.add_parser("report", help="View research reports")
    p_rep.add_argument("--latest", action="store_true", help="Show most recent report")
    p_rep.add_argument("--date", help="Report date (YYYY-MM-DD)")
    p_rep.add_argument(
        "--format", choices=["markdown", "json", "summary"],
        default="summary", help="Output format (default: summary)"
    )
    p_rep.set_defaults(func=cmd_report)

    # cache
    p_cache = sub.add_parser("cache", help="Manage fetch cache")
    p_cache.add_argument("--clear", action="store_true")
    p_cache.add_argument("--stats", action="store_true")
    p_cache.set_defaults(func=cmd_cache)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
