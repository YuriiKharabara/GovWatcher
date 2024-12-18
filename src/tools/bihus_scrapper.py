# SHOULD BE RAN SEPARATELY

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
import json
from tqdm import tqdm

class BihusParser:
    def __init__(self, base_url="https://bihus.info/wp-admin/admin-ajax.php", save_dir="./bihus_parsed_data", headers=None):
        self.base_url = base_url
        self.headers = headers
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def fetch_paginated_articles(self, until_date, posts_per_page=24):
        """Fetch articles until a specific date."""
        news_data = []
        offset = 0
        page = 0
        if isinstance(until_date, str):
            until_date = datetime.strptime(until_date, "%Y-%m-%d")
        while True:
            print(f"Fetching page {page}...")
            params = {
                "id": "",
                "post_id": "12",
                "slug": "news",
                "canonical_url": "https://bihus.info/news/",
                "posts_per_page": posts_per_page,
                "page": page,
                "offset": offset,
                "post_type": "post",
                "repeater": "template_1",
                "seo_start_page": "1",
                "preloaded": "false",
                "preloaded_amount": "0",
                "order": "DESC",
                "orderby": "date",
                "action": "alm_get_posts",
                "query_type": "standard",
            }
            response = requests.get(self.base_url, headers=self.headers, params=params)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}: {response.status_code}")
                break
            try:
                json_response = response.json()
                html_content = json_response.get("html", "")
                soup = BeautifulSoup(html_content, "html.parser")
                articles = soup.find_all("article")
                page_articles = []
                for article in tqdm(articles, desc=f"Page {page} Articles", unit="article"):
                    title_element = article.find("h2")
                    time_element = article.find("time")
                    link_element = article.find("a", href=True)
                    title = title_element.text.strip() if title_element else "No Title"
                    date_str = time_element["datetime"] if time_element else "1970-01-01"
                    article_date = datetime.strptime(date_str, "%Y-%m-%d")
                    link = link_element["href"] if link_element else "No Link"
                    if article_date < until_date:
                        print(f"Reached article before {until_date}. Stopping...")
                        news_data.extend(page_articles)
                        return news_data
                    page_articles.append({"date": date_str, "title": title, "link": link})
                if page_articles:
                    print(f"Page {page} - First Article:\n{page_articles[0]}")
                    print(f"Page {page} - Last Article:\n{page_articles[-1]}\n\n")
                news_data.extend(page_articles)
            except Exception as e:
                print(f"Error parsing response for page {page}: {e}")
                break
            offset += posts_per_page
            page += 1
        print(f"Fetched {len(news_data)} articles.")
        return news_data

    def fetch_article_content(self, link):
        """Fetch and clean the content of a single article."""
        try:
            response = requests.get(link, headers=self.headers)
            if response.status_code != 200:
                return f"Failed to fetch article: {response.status_code}"
            soup = BeautifulSoup(response.text, "html.parser")
            content_div = soup.find("div", class_="bi-single-content")
            if not content_div:
                return "No content found in the article"
            raw_content = content_div.get_text(separator="\n")
            clean_content = re.sub(r"\s*\n\s*", "\n", raw_content).strip()
            clean_content = re.sub(r"\n{2,}", "\n", clean_content)
            return clean_content
        except Exception as e:
            return f"Error: {str(e)}"

    def save_article_to_file(self, article):
        """Save a single article to a file."""
        date_str = datetime.strptime(article["date"], "%Y-%m-%d").strftime("%d-%m-%Y")
        base_filename = f"{date_str}.json"
        filepath = os.path.join(self.save_dir, base_filename)
        counter = 1
        while os.path.exists(filepath):
            filepath = os.path.join(self.save_dir, f"{date_str}_{counter}.json")
            counter += 1
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        print(f"Saved article to {filepath}")

    def parse_until_date(self, until_date, posts_per_page=24):
        """Parse articles until a specific date and save them."""
        articles = self.fetch_paginated_articles(until_date, posts_per_page)
        for article in tqdm(articles, desc="Processing each Articles", unit="article"):
            print(f"Fetching content for: {article['title']}")
            content = self.fetch_article_content(article["link"])
            article["content"] = content
            self.save_article_to_file(article)
        print("All articles have been processed and saved.")

if __name__ == "__main__":
    headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
            )
        }
    parser = BihusParser()
    parser.parse_until_date("2013-01-01", posts_per_page=100)
