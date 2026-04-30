"""Instagram competitor research pipeline.

Steps:
    1. ScrapeCompetitors - scrape reels from all tracked competitors
    2. ScoreAndRank - compute virality + engagement metrics and rank
    3. AnalyzeContent - extract hooks, themes, patterns from captions
    4. GenerateReport - save markdown + JSON report
"""

from pipeline.base import ResearchStep, ResearchPipeline


class ScrapeCompetitorsStep(ResearchStep):
    @property
    def name(self):
        return "Scrape Competitors"

    def execute(self, context):
        from instagram.scraper import scrape_all_competitors

        max_reels = context.get("reels_per_competitor", 30)
        cache = context.get("cache")

        reels = scrape_all_competitors(
            max_reels_per=max_reels, cache=cache
        )

        context["raw_reels"] = reels
        return context


class ScoreAndRankStep(ResearchStep):
    @property
    def name(self):
        return "Score & Rank"

    def execute(self, context):
        from instagram.scorer import score_and_rank

        reels = context["raw_reels"]
        top_n = context.get("top_n", 15)

        ranked = score_and_rank(reels, top_n=top_n)

        context["ranked_reels"] = ranked
        return context


class AnalyzeContentStep(ResearchStep):
    @property
    def name(self):
        return "Analyze Content"

    def execute(self, context):
        from instagram.analyzer import analyze_all, compute_insights

        ranked = context["ranked_reels"]
        analyzed = analyze_all(ranked)
        insights = compute_insights(analyzed)

        print(f"    Themes found: {', '.join(t for t, _ in insights['top_themes'][:5])}")
        print(f"    Top hooks: {', '.join(p for p, _ in insights['top_hook_patterns'][:3])}")
        print(f"    Avg caption length: {insights['avg_caption_length']} chars")

        context["analyzed_reels"] = analyzed
        context["insights"] = insights
        return context


class GenerateReportStep(ResearchStep):
    @property
    def name(self):
        return "Generate Report"

    def execute(self, context):
        from output.reporter import save_ig_reports

        analyzed = context["analyzed_reels"]
        insights = context["insights"]

        from instagram.scraper import load_competitors
        competitors = load_competitors()

        metadata = {
            "competitors": [c["username"] for c in competitors],
            "reels_per_competitor": context.get("reels_per_competitor", 30),
            "total_reels_found": len(context.get("raw_reels", [])),
            "top_n": context.get("top_n", 15),
        }

        md_path, json_path = save_ig_reports(analyzed, insights, metadata)
        print(f"    Report: {md_path}")

        context["report_md_path"] = md_path
        context["report_json_path"] = json_path
        return context


def create_instagram_research_pipeline():
    """Create the full Instagram competitor research pipeline."""
    return ResearchPipeline(
        name="Instagram Competitor Research",
        steps=[
            ScrapeCompetitorsStep(),
            ScoreAndRankStep(),
            AnalyzeContentStep(),
            GenerateReportStep(),
        ],
    )
