import gradio as gr
from dotenv import load_dotenv

from tools.ScrapingTool import ScrapingTool
from tools.DeclarationAnalysisTool import DeclarationAnalysisTool

load_dotenv()


def analyze_url(url: str):
    scraping_tool = ScrapingTool()
    declarations_data = scraping_tool.get_declarations_data(url)

    declaration_analysis_tool = DeclarationAnalysisTool()
    declarations_analysis = declaration_analysis_tool.analyze_declarations(declarations_data)

    # TODO: Implement Bihus tool and call it here

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
