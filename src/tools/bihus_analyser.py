import os
import json
from fuzzywuzzy import fuzz
from tqdm import tqdm
import json
from textwrap import dedent
import openai
from src.tools.openai_bihus import openai_request

class ArticleAnalyzer:
    def __init__(self, data_dir="./bihus_modified_identity_data"):
        """
        Initialize the ArticleAnalyzer class.

        :param data_dir: Path to the folder containing JSON files.
        :param openai_interface: Placeholder function to integrate with OpenAI for analysis.
        """
        client = openai.OpenAI()
        self.data_dir = data_dir
        self.articles = []
        self._client = client
        self._load_articles()

    def _load_articles(self):
        """Load all articles from the data directory."""
        for file in os.listdir(self.data_dir):
            if file.endswith(".json"):
                file_path = os.path.join(self.data_dir, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    self.articles.append(json.load(f))
        print(f"Loaded {len(self.articles)} articles.")

    def is_fuzzy_match(self, target, candidate, threshold=75):
        """Check if two strings match based on a fuzzy matching threshold."""
        return fuzz.ratio(target, candidate) >= threshold

    def analyze_person(self, target_name):
        """
        Analyze articles mentioning a specific person and calculate metrics.

        :param target_name: Full name of the person to analyze.
        :return: Dictionary with aggregated metrics and detailed article analysis.
        """
        self.target_name = target_name
        mentioned_articles = []
        for article in self.articles:
            persons = article.get("entities_included", {}).get("PER", [])
            for person in persons:
                if self.is_fuzzy_match(target_name, person):
                    mentioned_articles.append(article)
                    break
        print(f"{target_name} was mentioned in {len(mentioned_articles)} articles.")

        detailed_results = []
        for article in tqdm(mentioned_articles, desc="Analyzing articles", unit="article"):
            result = self._analyze_article(article)
            detailed_results.append(result)
        aggregated_metrics = self._aggregate_metrics(detailed_results)
        return {
            "target_name": target_name,
            "aggregated_metrics": aggregated_metrics,
            "detailed_results": detailed_results
        }

    def _analyze_article(self, article):
        """
        Analyze a single article to extract specific metrics.

        :param article: Article data (dict).
        :return: Extracted metrics for the article.
        """
        response = openai_request(article=article, person_name=self.target_name, client=self._client)
        return {
            "title": article["title"],
            "link": article["link"],
            "negative_mentions": response.get("negative_mentions", False),
            "suspicious_activity": response.get("suspicious_activity", False),
            "suspicious_gifts_and_other": response.get("suspicious_gifts_and_other", False),
            "finished_investigation": response.get("finished_investigation", False)
        }

    def _aggregate_metrics(self, detailed_results):
        """
        Aggregate metrics from individual article analyses.

        :param detailed_results: List of individual article results.
        :return: Aggregated metrics.
        """
        metrics = {
            "negative_mentions_count": 0,
            "suspicious_activity_count": 0,
            "suspicious_gifts_and_other": False,
            "finished_investigation_count": 0,
            "final_score": {}
        }

        for result in detailed_results:
            metrics["negative_mentions_count"] += 1 if result["negative_mentions"] else 0
            metrics["suspicious_activity_count"] += 1 if result["suspicious_activity"] else 0
            metrics["suspicious_gifts_and_other"] = metrics["suspicious_gifts_and_other"] or result["suspicious_gifts_and_other"]
            metrics["finished_investigation_count"] += 1 if result["finished_investigation"] else 0

        metrics["final_score"] = {
            "negative_mentions_score": 0 if metrics["negative_mentions_count"] == 0 else (1 if metrics["negative_mentions_count"] <= 5 else 2),
            "suspicious_activity_score": 0 if metrics["suspicious_activity_count"] == 0 else (1 if metrics["suspicious_activity_count"] <= 3 else 2),
            "suspicious_gifts_and_other": metrics["suspicious_gifts_and_other"],
            "finished_investigation": metrics["finished_investigation_count"] > 0
        }

        return metrics

