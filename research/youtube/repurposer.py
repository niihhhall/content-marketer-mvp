"""Repurpose YouTube videos into Instagram carousels."""

import re
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript(video_id):
    """Fetch transcript for a YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([t["text"] for t in transcript_list])
        return full_text
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None


def structure_into_slides(transcript_text):
    """
    Agentic step: This would normally be handled by the LLM.
    Here we provide a helper to clean and prepare the text for the agent.
    """
    # Clean text
    text = re.sub(r"\[.*?\]", "", transcript_text)
    text = re.sub(r"\s+", " ", text).strip()
    
    # Return first 5000 chars for the agent to process
    return text[:5000]


def generate_carousel_config(topic_or_url, brand_config):
    """
    Main entry point for the agent to generate a carousel config.
    The agent should call this, then use the results to write config.json.
    """
    if "youtube.com" in topic_or_url or "youtu.be" in topic_or_url:
        video_id = extract_video_id(topic_or_url)
        if video_id:
            transcript = get_transcript(video_id)
            if transcript:
                return {
                    "source": "youtube",
                    "video_id": video_id,
                    "content": structure_into_slides(transcript)
                }
    
    return {
        "source": "topic",
        "content": topic_or_url
    }
