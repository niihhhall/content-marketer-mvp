#!/usr/bin/env python3
"""
Instagram Pro CLI
Unified entry point for research and carousel generation.
"""

import argparse
import os
import sys
from pathlib import Path

# Add research/ to path
sys.path.append(str(Path(__file__).parent / "research"))

def run_research(args):
    """Run the Instagram research pipeline."""
    from pipeline.instagram_research import create_instagram_research_pipeline
    from cache.store import CacheStore
    
    print("🚀 Starting Instagram Competitor Research...")
    pipeline = create_instagram_research_pipeline()
    
    context = {
        "reels_per_competitor": args.limit,
        "top_n": args.top,
        "cache": CacheStore()
    }
    
    pipeline.run(context)
    print("\n✅ Research complete!")

def run_carousel(args):
    """Generate a carousel from a topic or URL."""
    print(f"🎨 Generating carousel for: {args.input}")
    # This will be implemented with an agentic loop or a script
    # For now, we'll placeholder the logic
    print("Note: This command triggers the agentic content creation flow.")
    print("1. Fetching context (YouTube/Web)...")
    print("2. Writing slides...")
    print("3. Rendering PNGs...")
    
    # In a real skill, we might call the renderer after the agent writes the config
    # For now, just a message.
    print("Logic pending integration with Antigravity agentic planning.")

def main():
    parser = argparse.ArgumentParser(description="Instagram Pro Automation")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")
    
    # Research command
    research_parser = subparsers.add_parser("research", help="Run competitor research")
    research_parser.add_argument("--limit", type=int, default=30, help="Reels per competitor")
    research_parser.add_argument("--top", type=int, default=15, help="Number of top reels to analyze")
    
    # Carousel command
    carousel_parser = subparsers.add_parser("carousel", help="Generate a carousel")
    carousel_parser.add_argument("input", help="Topic or YouTube URL")
    carousel_parser.add_argument("--brand", default="default", help="Brand name to use")
    
    args = parser.parse_args()
    
    if args.command == "research":
        run_research(args)
    elif args.command == "carousel":
        run_carousel(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
