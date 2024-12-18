import gradio as gr
from dotenv import load_dotenv

from src.tools.declaration_scrapping import ScrapingTool
from src.tools.declaration_analysis import DeclarationAnalysisTool
from src.tools.bihus_analyser import ArticleAnalyzer
load_dotenv()


def analyze_url(url: str):
    scraping_tool = ScrapingTool()
    declarations_data = scraping_tool.get_declarations_data(url)

    declaration_analysis_tool = DeclarationAnalysisTool()
    declarations_analysis = declaration_analysis_tool.analyze_declarations(declarations_data)

    # TODO: Implement Bihus tool and call it here
    bihus_analysis_tool = ArticleAnalyzer()
    bihus_analysis = ArticleAnalyzer.analyze_person(declarations_data["full_name"])


    # TODO: Implement score calculation logic



    # TODO: Implement report generation and call it here

    return declarations_analysis


demo = gr.Interface(
# TODO: Implement report presentation in Gradio
    fn=analyze_url,
    inputs=gr.Textbox(label="Enter URL"),
    outputs=gr.JSON(label="Analysis Result"),
    title="Declaration Analysis Tool",
    description="Enter a URL to a politician's declarations page and get an analysis."
)

if __name__ == "__main__":
    demo.launch()
