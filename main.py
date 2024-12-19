import gradio as gr
from dotenv import load_dotenv

from src.tools.declaration_scrapping import ScrapingTool
from src.tools.declaration_analysis import DeclarationAnalysisTool
from src.tools.bihus_analyser import ArticleAnalyzer
from src.tools.report_generator import ReportGenerator
load_dotenv()


def analyze_url(url: str):
    scraping_tool = ScrapingTool()
    declarations_data = scraping_tool.extract_declarations_data(url)
    print("scrapped declarations")

    declaration_analysis_tool = DeclarationAnalysisTool()
    declarations_analysis = declaration_analysis_tool.analyze_declarations(declarations_data)
    print("analyzed declarations")

    bihus_analysis_tool = ArticleAnalyzer()
    bihus_analysis = bihus_analysis_tool.analyze_person(declarations_data[0]["politician_name"] + " " + declarations_data[0]["politician_surname"])
    print("analyzed bihus")

    score = 0
    for key, details in declarations_analysis.items():
        value = details.get("value")
        if isinstance(value, bool):
            score += int(value)
        elif isinstance(value, (int, float)):
            score += value

    bihus_final_score = bihus_analysis["aggregated_metrics"].get("final_score", {})
    for key, value in bihus_final_score.items():
        if isinstance(value, bool):
            score += int(value)
        elif isinstance(value, (int, float)):
            score += value

    print("final score", score)

    report_gen = ReportGenerator(bihus_analysis, declarations_analysis, score)
    report = report_gen.generate_report()

    gauge = report_gen.create_score_gauge()

    combined_data = {
        "declarations_analysis": declarations_analysis,
        "bihus_analysis": bihus_analysis,
        "final_score": score
    }

    return combined_data, report, gauge

demo = gr.Interface(
    fn=analyze_url,
    inputs=gr.Textbox(label="Enter URL"),
    outputs=[
        gr.JSON(label="Analysis Result"),
        gr.HTML(label="Summary Report"),
        gr.Plot(label="Suspicion Gauge")
    ],
    title="Declaration Analysis Tool",
    description="Enter a URL to a politician's declarations page and get an analysis."
)

if __name__ == "__main__":
    demo.launch()
