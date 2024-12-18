from typing import List, Optional
import openai
import requests
from bs4 import BeautifulSoup
from textwrap import dedent
import json

from const import SCRAPING_RESPONSE_SCHEMA, SCRAPING_PROMPT


class ScrapingTool:
    def __init__(self):
        self.client = openai.OpenAI()
        self.model = "gpt-4o-2024-08-06"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            'referer': "https://youcontrol.com.ua/"
        }
        self.response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "declaration_extraction",
                "description": "Fetches the declarations data from the HTML",
                "strict": True,
                "schema": SCRAPING_RESPONSE_SCHEMA
            }
        }
        self.prompt = SCRAPING_PROMPT

    def get_declarations_urls(self, url: str) -> List[str]:
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            link_elements = soup.select("a[href]")
            urls = []
            for link_element in link_elements:
                url = link_element['href']
                if "/catalog/individuals/declaration/" in url:
                    urls.append(url)
        else:
            print(f"Failed to fetch the webpage. Status code: {response.status_code}")
            urls = []
        return urls

    def scrape_declaration(self, urls: List[str]) -> List[str]:
        wrappers = []
        for url in urls:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                wrapper_div = soup.find('div', class_='wrapper')
                wrappers.append(wrapper_div)
            else:
                print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return wrappers

    def get_response(self, question):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": dedent(self.prompt)
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            response_format=self.response_format)

        event = response.choices[0].message
        return event.content

    def get_declarations_data(self, url) -> Optional[List[dict]]:
        declarations_urls = self.get_declarations_urls(url)
        if not declarations_urls:
            print("Failed to fetch declarations")
            return None
        declarations_urls = ["https://youcontrol.com.ua" + url for url in declarations_urls[::-1]]

        scraped_declaration = self.scrape_declaration(declarations_urls)
        if not scraped_declaration:
            print("Failed to scrape declarations")
            return None

        results = []
        for wrapper in scraped_declaration:
            question = f"Extract information from this refined HTML response {wrapper}"
            chat_response = self.get_response(question)
            result = json.loads(chat_response)
            results.append(result)
        if not results:
            print("Failed to extract information")

        return results
