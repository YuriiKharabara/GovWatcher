from openai import OpenAI
import plotly.graph_objects as go
from markdown import markdown
import gradio as gr


class ReportGenerator:
    """
    Generate Technical Reports Regarding Suspicious Activity
    """
    def __init__(self, bihus_analysis, declarations_analysis, score):
        self.bihus_analysis = bihus_analysis
        self.declarations_analysis = declarations_analysis
        self.score = score
        self.client = OpenAI()

    def generate_report(self):
        """
        Bihus articles section
        """
        bihus_articles = self.bihus_analysis.get("detailed_results", [])
        articles_html = ""
        if bihus_articles:
            articles_html += "<div class='bihus-section-title'>Media Mentions and Investigations:</div><ul class='bihus-list'>"
            for article in bihus_articles:
                title = article.get("title", "No title")
                link = article.get("link", "#")
                articles_html += f"<li><a href='{link}' target='_blank'>{title}</a></li>"
            articles_html += "</ul>"

        # Wrap the textual report and bihus articles in styled HTML
        html_report = f"""
<html>
<head>
<style>
    body {{
        font-family: "Helvetica", sans-serif;
    }}
    .report-container {{
        border: 1px solid #ddd;
        padding: 30px;
        border-radius: 8px;
        max-width: 600px;
        margin: 20px auto;
    }}
    .report-title {{
        font-size: 1.5em;
        margin-bottom: 10px;
        color: #333;
        font-weight: bold;
    }}
    .report-content {{
        font-size: 1em;
        line-height: 1.6;
        color: #121212;
    }}
    .highlight {{
        background: #ffeeba;
        padding: 5px;
        border-radius: 3px;
        font-weight: bold;
    }}
    .bihus-section-title {{
        margin-top: 20px;
        font-weight: bold;
        font-size: 1.2em;
    }}
    .bihus-list {{
        list-style-type: none;
        padding-left: 0;
        margin-top: 10px;
    }}
    .bihus-list li {{
        margin-bottom: 5px;
    }}
    .bihus-list li a {{
        color: #2e6da4;
        text-decoration: none;
    }}
    .bihus-list li a:hover {{
        text-decoration: underline;
    }}
</style>
</head>
<body>
<div class="report-container">
    <div class="report-title">Suspicion Analysis Report</div>
    <div class="report-content">{self._generate_text_report()}</div>
    {articles_html}
</div>
</body>
</html>
"""
        return html_report

    def _generate_text_report(self):
        """
        Generate a textual summary of the findings using OpenAI's API.
        """
        suspicious_indicators = []
        for key, details in self.declarations_analysis.items():
            val = details.get("value", None)
            explanation = details.get("explanation", "")
            if val:
                suspicious_indicators.append(f"- {key}: {explanation}")
        
        bihus_details = self.bihus_analysis.get("aggregated_metrics", {})
        negative_mentions = bihus_details.get("negative_mentions_count", 0)
        suspicious_activity_count = bihus_details.get("suspicious_activity_count", 0)
        suspicious_gifts = bihus_details.get("suspicious_gifts_and_other", False)
        finished_investigations = bihus_details.get("finished_investigation_count", 0)

        prompt = f"""
You are a fraud/corruption investigator. Summarize the suspicious indicators found in a set of politician's declarations and media investigations.

Politician name: {self.bihus_analysis.get('target_name', 'Unknown')}

Declarations suspicious analysis:
{"".join(suspicious_indicators)}

Bihus analysis:
- Negative mentions count: {negative_mentions}
- Suspicious activity count: {suspicious_activity_count}
- Suspicious gifts and other: {suspicious_gifts}
- Finished investigations: {finished_investigations}

Final Combined Score: {self.score}

Create a concise, investigative summary report that highlights key suspicious findings and their potential implications.
    """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a helpful assistant that creates summary reports."},
                    {"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
        return markdown(summary)

    def create_score_gauge(self):
        """
        Create a gauge visualization of the score.
        """
        max_score = 10

        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = self.score,
            title = {'text': "Suspicion Score"},
            gauge = {
                'axis': {'range': [0, max_score]},
                'bar': {'color': "darkred"},
                'steps': [
                    {'range': [0, 2], 'color': 'lightgreen'},
                    {'range': [2, 4], 'color': 'green'},
                    {'range': [4, 6], 'color': 'yellow'},
                    {'range': [6, 8], 'color': 'orange'},
                    {'range': [8, max_score], 'color': 'red'}
                ]
            }
        ))

        fig.update_layout(height=300)
        return fig
