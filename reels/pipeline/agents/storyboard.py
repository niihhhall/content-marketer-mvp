"""Storyboard Agent: use Claude to plan the visual timeline of the reel."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import List, Dict

import anthropic

PIPELINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(PIPELINE_DIR)

SYSTEM_PROMPT = """You are an expert Instagram Reels Director. Your job is to create a professional, high-energy visual storyboard for a 9:16 vertical reel.

STORYBOARD RULES:
1. PACE: Every segment should be between 1.0 and 3.0 seconds. 
2. VARIETY: Alternate between different asset types. Avoid showing the same asset twice in a row.
3. MOTION FIRST: Prioritize video clips over static screenshots. Aim for 60% video.
4. SEMANTIC MATCH: Every visual must directly relate to what is being said in the transcript at that moment.
5. TYPES: Use these types for segments:
   - 'video': Use an existing approved video clip.
   - 'screenshot': Use an existing approved image.
   - 'image_needed': If the script mentions something specific but no asset exists (e.g. "Snoop Dogg", "Tom Brady"). The Image Resolver will download this.
   - 'veo_needed': If you need a cinematic cinematic shot but no asset exists. The Veo Agent will generate this.
6. FORMAT: Output a JSON object with a 'segments' array.

JSON SCHEMA:
{
  "segments": [
    {
      "startSec": 0.0,
      "endSec": 2.5,
      "type": "video | screenshot | image_needed | veo_needed",
      "asset_path": "path/to/asset.mp4" (only if type is video or screenshot),
      "label": "short descriptive label",
      "image_query": "search query for Wikipedia" (only if type is image_needed),
      "veo_prompt": "cinematic prompt" (only if type is veo_needed),
      "framing": { "objectPosition": "center center", "scaleFrom": 1.0, "scaleTo": 1.05 },
      "_speech": "the words spoken during this segment"
    }
  ]
}
"""


def plan_storyboard(reel_id: str, tool_name: str, script: str, transcript: dict, assets: list, model: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # Prepare asset summary for Claude
    approved_assets = [a for a in assets if a.get("approved")]
    asset_list = []
    for a in approved_assets:
        asset_list.append({
            "id": a["id"], "type": a["type"], "path": a["path"],
            "quality": a["quality_score"], "duration": a.get("duration_sec")
        })

    user_prompt = f"""Create a storyboard for a reel about: {tool_name}
Script: {script}

Transcript (with timestamps):
{json.dumps(transcript['words'], indent=1)}

Available Approved Assets:
{json.dumps(asset_list, indent=1)}

Constraints:
- Reel ID: {reel_id}
- Target duration: {transcript['words'][-1]['end']} seconds.
- No gaps between segments.
- Segments must align with transcript timestamps.
- Use 'veo_needed' for cinematic gaps.
- Use 'image_needed' for specific person/brand mentions.

Output ONLY the JSON storyboard."""

    print(f"  Calling Claude ({model})...")
    resp = client.messages.create(
        model=model,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    )

    content = resp.content[0].text
    # Extract JSON
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "{" in content:
        content = content[content.find("{"):content.rfind("}")+1]

    return json.loads(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reel-id", required=True)
    parser.add_argument("--model", default="claude-3-5-sonnet-20240620")
    args = parser.parse_args()

    from pipeline.agents.pipeline_state import PipelineState
    state = PipelineState(args.reel_id)
    
    manifest = state.get_output("curate")
    if not manifest:
        print("Error: No asset manifest found. Run curate first.")
        return

    # Load transcript
    transcript_path = state.get_config("transcript_path")
    if not os.path.exists(transcript_path):
        # Try local path
        transcript_path = os.path.join(PROJECT_DIR, "public", "avatars", os.path.basename(transcript_path))
    
    with open(transcript_path) as f:
        transcript = json.load(f)

    storyboard = plan_storyboard(
        args.reel_id, state.get_config("tool_name"),
        state.get_config("script"), transcript,
        manifest["assets"], args.model
    )

    output_path = os.path.join(state.reel_dir, "storyboard.json")
    with open(output_path, "w") as f:
        json.dump(storyboard, f, indent=2)

    summary = {"segments": len(storyboard.get("segments", []))}
    state.complete_stage("storyboard", "storyboard.json", summary)
    print(f"  Storyboard planned: {summary['segments']} segments.")


if __name__ == "__main__":
    main()
