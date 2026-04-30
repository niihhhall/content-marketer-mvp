"""Scheduler Agent: upload video and schedule via Metricool API."""

import argparse
import json
import os
import requests
import sys
from datetime import datetime, timedelta

PIPELINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "metricool_config.json")
METRICOOL_API = "https://app.metricool.com/api"


def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Missing {CONFIG_PATH}")
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    # Validation
    for key in ["api_token", "user_id", "blog_id"]:
        val = config.get(key, "")
        if not val or val.startswith("YOUR_"):
            # Try env var as fallback
            env_val = os.environ.get(f"METRICOOL_{key.upper()}")
            if env_val:
                config[key] = env_val
            else:
                raise ValueError(f"Set your {key} in metricool_config.json or METRICOOL_{key.upper()} env var")
    return config


def upload_to_tmpfiles(video_path):
    """Upload a video file to tmpfiles.org, return a direct download URL."""
    print(f"  Uploading {os.path.basename(video_path)} to tmpfiles.org...")
    with open(video_path, "rb") as f:
        r = requests.post(
            "https://tmpfiles.org/api/v1/upload",
            files={"file": f},
            timeout=180,
        )

    if r.status_code == 200:
        raw_url = r.json()["data"]["url"]
        # Convert to direct download link
        return raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
    else:
        raise Exception(f"Upload failed: {r.status_code} - {r.text}")


def schedule_reel(video_url, caption, schedule_time, config):
    """Schedule an Instagram Reel via Metricool API."""
    print(f"  Scheduling for {schedule_time.strftime('%Y-%m-%d %H:%M')} ({config['timezone']})...")
    
    payload = {
        "text": caption,
        "publicationDate": {
            "dateTime": schedule_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "timezone": config["timezone"],
        },
        "draft": False,
        "autoPublish": True,
        "saveExternalMediaFiles": True,
        "providers": [{"network": "INSTAGRAM"}],
        "instagramData": {
            "type": "TRIAL_REEL",
            "shareTrialAutomatically": False,
        },
        "media": [video_url],
    }

    r = requests.post(
        f"{METRICOOL_API}/v2/scheduler/posts",
        headers={
            "X-Mc-Auth": config["api_token"],
            "Content-Type": "application/json",
        },
        params={
            "userId": config["user_id"],
            "blogId": config["blog_id"],
        },
        json=payload,
        timeout=30,
    )

    if r.status_code in [200, 201]:
        return r.json().get("data", {})
    else:
        raise Exception(f"Metricool post failed ({r.status_code}): {r.text[:500]}")


def main():
    parser = argparse.ArgumentParser(description="Schedule Reel via Metricool")
    parser.add_argument("--reel-id", required=True)
    parser.add_argument("--video", help="Path to video file (if not in pipeline output)")
    parser.add_argument("--caption", help="Caption text (overrides script)")
    parser.add_argument("--delay-hours", type=float, default=1.0, help="Hours from now to schedule")
    parser.add_argument("--time", help="ISO format time (YYYY-MM-DDTHH:MM:S)")
    args = parser.parse_args()

    from pipeline.agents.pipeline_state import PipelineState
    state = PipelineState(args.reel_id)
    
    config = load_config()

    # 1. Determine video path
    video_path = args.video
    if not video_path:
        # Default to pipeline render
        reels_dir = os.path.dirname(PIPELINE_DIR)
        video_path = os.path.join(reels_dir, "renders", f"{args.reel_id}_render.mp4")
    
    if not os.path.exists(video_path):
        print(f"Error: Video not found at {video_path}")
        sys.exit(1)

    # 2. Determine caption
    caption = args.caption or state.get_config("script") or f"New Reel: {state.get_config('tool_name')}"

    # 3. Determine schedule time
    if args.time:
        publish_time = datetime.fromisoformat(args.time)
    else:
        publish_time = datetime.now() + timedelta(hours=args.delay_hours)

    # 4. Execute
    try:
        url = upload_to_tmpfiles(video_path)
        print(f"  Direct Link: {url}")
        
        result = schedule_reel(url, caption, publish_time, config)
        print(f"\n  SUCCESS! Scheduled via Metricool.")
        print(f"  Post ID: {result.get('id')}")
        
        state.complete_stage("review", f"{args.reel_id}_scheduled.json", {
            "post_id": result.get("id"),
            "publish_time": publish_time.isoformat(),
            "metricool_url": f"https://app.metricool.com/scheduler/blog/{config['blog_id']}"
        })
        
    except Exception as e:
        print(f"\n  FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
