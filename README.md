# 📸 Instagram Pro: Automation & Research Engine

![Banner](./assets/banner.png)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Instagram Pro** is a high-agency, multi-agent production system designed for automated competitor analysis, content research, and high-fidelity carousel generation.

---

## 🚀 Key Features

- **🔍 Competitor Research:** Scrape and analyze top-performing reels from any competitor.
- **📊 Advanced Analytics:** Detect hooks, themes, and content patterns using intelligent classification.
- **🎨 Carousel Engine:** Convert YouTube transcripts or topics into stunning Instagram carousels.
- **⚡ Performance Scoring:** Automated ranking of reels based on engagement and viral potential.
- **🏢 Brand Management:** Easily setup and manage multiple brand identities with custom palettes and typography.

---

## 🛠️ Tech Stack

- **Core Logic:** Python 3.8+
- **Data Acquisition:** DataPrism & Apify REST APIs
- **Content Research:** YouTube Transcript API
- **Processing:** Multi-agent pipeline architecture

---

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/content-marketer-mvp.git
   cd content-marketer-mvp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables:**
   Create a `.env` file or export your API keys:
   ```bash
   export DATAPRISM_API_KEY="your_key_here"
   export APIFY_TOKEN="your_token_here"
   ```

---

## 📖 Usage Guide

### 1. Competitor Research
Analyze top reels from your niche:
```bash
python ig_pro.py research --limit 30 --top 15
```

### 2. Brand Setup
Initialize a new brand configuration:
```bash
python manager.py setup mybrand
```

### 3. Carousel Generation
Create a carousel from a YouTube video:
```bash
python ig_pro.py carousel "https://youtube.com/watch?v=..." --brand mybrand
```

---

## 📂 Project Structure

```
.
├── brands/             # Brand configuration JSONs
├── research/           # Core research & scraping logic
│   ├── instagram/      # IG scraper and analyzer
│   ├── youtube/        # YouTube transcript repurposer
│   └── pipeline/       # Research pipeline orchestration
├── ig_pro.py           # Unified CLI entry point
├── manager.py          # Brand and design management
└── requirements.txt    # Project dependencies
```

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  Built with ❤️ by <b>Antigravity</b>
</p>
