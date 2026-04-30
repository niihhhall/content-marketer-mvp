#!/usr/bin/env python3
"""Unified CLI for the AI Reels Pipeline."""

import argparse
import os
import subprocess
import sys

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.join(PIPELINE_DIR, "agents")
REELS_DIR = os.path.dirname(PIPELINE_DIR)

def run_agent(agent_name: str, args: list):
    script = os.path.join(AGENTS_DIR, f"{agent_name}.py")
    cmd = [sys.executable, script] + args
    print(f"\n>>> Running {agent_name}...")
    env = os.environ.copy()
    env["PYTHONPATH"] = REELS_DIR + os.pathsep + env.get("PYTHONPATH", "")
    subprocess.run(cmd, check=True, env=env)

def main():
    parser = argparse.ArgumentParser(description="AI Reels Pipeline CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Init
    p_init = subparsers.add_parser("init")
    p_init.add_argument("reel_id")
    p_init.add_argument("--tool", required=True)
    p_init.add_argument("--transcript", required=True)
    p_init.add_argument("--avatar", required=True)
    p_init.add_argument("--script", default="")

    # Stage runners
    p_curate = subparsers.add_parser("curate")
    p_curate.add_argument("reel_id")
    p_curate.add_argument("--extra-dir", action="append")

    p_story = subparsers.add_parser("storyboard")
    p_story.add_argument("reel_id")

    p_assemble = subparsers.add_parser("assemble")
    p_assemble.add_argument("reel_id")

    # Render
    p_render = subparsers.add_parser("render")
    p_render.add_argument("reel_id")
    p_render.add_argument("--out", help="Output filename")

    # Schedule
    p_schedule = subparsers.add_parser("schedule")
    p_schedule.add_argument("reel_id")
    p_schedule.add_argument("--video", help="Path to video file")
    p_schedule.add_argument("--caption", help="Caption text")
    p_schedule.add_argument("--delay", type=float, default=1.0, help="Hours from now")

    args = parser.parse_args()

    if args.command == "init":
        run_agent("pipeline_state", [args.reel_id, "--init", "--tool", args.tool,
                                     "--transcript", args.transcript, "--avatar", args.avatar,
                                     "--script", args.script])
    
    elif args.command == "curate":
        extra = []
        if args.extra_dir:
            for d in args.extra_dir: extra += ["--extra-dir", d]
        run_agent("asset_curator", ["--reel-id", args.reel_id, "--tool", "DUMMY"] + extra)
        
    elif args.command == "storyboard":
        run_agent("storyboard", ["--reel-id", args.reel_id])

    elif args.command == "assemble":
        run_agent("assembler", ["--reel-id", args.reel_id])

    elif args.command == "schedule":
        s_args = ["--reel-id", args.reel_id, "--delay-hours", str(args.delay)]
        if args.video: s_args += ["--video", args.video]
        if args.caption: s_args += ["--caption", args.caption]
        run_agent("scheduler", s_args)

    elif args.command == "render":
        # Load config and run remotion
        from agents.pipeline_state import PipelineState
        state = PipelineState(args.reel_id)
        config_path = os.path.join(state.reel_dir, "reel-config.json")
        if not os.path.exists(config_path):
            print("Error: reel-config.json not found. Run assemble first.")
            return
        
        output_name = args.out or f"{args.reel_id}_render.mp4"
        output_path = os.path.join(REELS_DIR, "renders", output_name)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print(f"\n>>> Rendering with Remotion...")
        # Note: We pass props as a JSON string
        with open(config_path) as f:
            props = json.load(f)
        
        cmd = [
            "npx", "remotion", "render", "DynamicReel", output_path,
            "--props", json.dumps({"config": props})
        ]
        subprocess.run(cmd, cwd=REELS_DIR, check=True)
        print(f"\nDone! Render saved to: {output_path}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
