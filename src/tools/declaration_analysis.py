from typing import List
import openai
from textwrap import dedent
import json

from src.const import DECLARATIONS_ANALYSIS_RESPONSE_SCHEMA, DECLARATIONS_ANALYSIS_PROMPT


class DeclarationAnalysisTool:
    def __init__(self):
        self.client = openai.OpenAI()
        self.model = "gpt-4o-2024-08-06"
        self.response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "declaration_analysis",
                "description": "Analyzes the declarations and checks for corruption",
                "strict": True,
                "schema": DECLARATIONS_ANALYSIS_RESPONSE_SCHEMA
            }
        }
        self.prompt = DECLARATIONS_ANALYSIS_PROMPT

    def get_response(self, declarations_data_str):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": dedent(self.prompt.format(declarations_data=declarations_data_str))
                },
            ],
            response_format=self.response_format,
            temperature=0
        )

        event = response.choices[0].message
        return event.content

    def analyze_declarations(self, declarations_data: List[dict]):
        declarations_data_str = json.dumps(declarations_data, ensure_ascii=False, indent=4)
        chat_response = self.get_response(declarations_data_str)
        result = json.loads(chat_response)
        return result
