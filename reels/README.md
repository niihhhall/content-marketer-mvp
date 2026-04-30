# AI Reels Pipeline

A professional Instagram Reels production pipeline using AI avatars, automated B-roll curation, and Remotion rendering.

## Directory Structure
- `src/`: Remotion (React) components and video logic.
- `heygen/`: Scripts for avatar generation and Whisper transcription.
- `pipeline/`: Python agents for storyboard planning and asset management.
- `public/`: Static assets (avatars, broll, logos).

## Quick Start

### 1. Preparation
Place your B-roll clips in `public/broll/clips/` and tool screenshots in `public/broll/topics/{tool-name}/`.

### 2. Initial Setup
```bash
cd reels
npm install
# Set your ANTHROPIC_API_KEY and HEYGEN_API_KEY
```

### 3. Run the Pipeline
```bash
# Initialize a new reel
python pipeline/cli.py init my-reel-01 --tool "Claude Code" --transcript "public/avatars/transcript.json" --avatar "avatar.mp4" --script "Hello world..."

# Curate assets (scans folders and grades quality)
python pipeline/cli.py curate my-reel-01

# Plan storyboard (calls Claude 3.5 Sonnet)
python pipeline/cli.py storyboard my-reel-01

# Assemble Remotion config
python pipeline/cli.py assemble my-reel-01

# Render final video
python pipeline/cli.py render my-reel-01

# Schedule via Metricool
python pipeline/cli.py schedule my-reel-01 --delay 24
```

## Features
- **Split-Screen Design**: Dynamic B-roll on top, AI Avatar on bottom.
- **Smart Captions**: Word-level synced captions with gradient backgrounds.
- **Quality Gates**: Asset curator rejects blurry or dark footage.
- **AI Storyboarding**: Claude plans the visual timing based on the transcript.
- **Automated Scheduling**: One-click upload and schedule via Metricool API.
- **Ken Burns Effect**: Automatic smooth zooming for screenshots.
