"""Assembler Agent: combine all stage outputs into a final Remotion ReelConfig."""

import argparse
import json
import os
from datetime import datetime, timezone

PIPELINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(PIPELINE_DIR)

def assemble_reel(reel_id: str, state) -> dict:
    storyboard = state.get_output("storyboard")
    transcript = {}
    with open(state.get_config("transcript_path")) as f:
        transcript = json.load(f)

    # 1. Map broll segments
    broll_segments = []
    for seg in storyboard.get("segments", []):
        path = seg.get("asset_path", "")
        if not path: continue
        
        broll = {
            "startSec": seg["startSec"],
            "endSec": seg["endSec"],
            "objectPosition": seg.get("framing", {}).get("objectPosition", "center center"),
            "scaleFrom": seg.get("framing", {}).get("scaleFrom", 1.0),
            "scaleTo": seg.get("framing", {}).get("scaleTo", 1.05),
        }
        if path.endswith((".mp4", ".mov", ".webm")):
            broll["video"] = os.path.basename(path)
        else:
            broll["image"] = path
        broll_segments.append(broll)

    # 2. Map caption chunks
    # We group words into chunks of ~3-5 words or based on natural pauses
    caption_chunks = []
    words = transcript.get("words", [])
    chunk_size = 4
    for i in range(0, len(words), chunk_size):
        group = words[i:i+chunk_size]
        caption_chunks.append({
            "text": " ".join([w["word"] for w in group]).upper(),
            "startSec": group[0]["start"],
            "endSec": group[-1]["end"] + 0.1,
        })

    # 3. Create Scene configs (placeholders for now)
    scenes = []
    
    # 4. Final Config
    duration_frames = int(transcript["words"][-1]["end"] * 25) + 5
    
    config = {
        "id": reel_id,
        "duration": duration_frames,
        "avatarSrc": os.path.basename(state.get_config("avatar_src")),
        "avatarMarginTop": -280,
        "brollSegments": broll_segments,
        "captionChunks": caption_chunks,
        "scenes": scenes,
        "crossfadeFrames": 8
    }
    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reel-id", required=True)
    args = parser.parse_args()

    from pipeline.agents.pipeline_state import PipelineState
    state = PipelineState(args.reel_id)
    
    config = assemble_reel(args.reel_id, state)

    output_path = os.path.join(state.reel_dir, "reel-config.json")
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)

    # Also copy to public/ for Remotion to see it if needed
    # (Actually Root.tsx uses it via props, but we'll save it for reference)

    summary = {
        "broll_segments": len(config["brollSegments"]),
        "caption_chunks": len(config["captionChunks"]),
        "duration_frames": config["duration"]
    }
    state.complete_stage("assemble", "reel-config.json", summary)
    print(f"  Reel assembled: {summary['duration_frames']} frames.")


if __name__ == "__main__":
    main()
