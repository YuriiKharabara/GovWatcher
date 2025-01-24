from textwrap import dedent
import openai
import json

def openai_request(article, person_name, client):
    json_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "article_analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "negative_mentions": {"type": "boolean", "description": "Indicates if the person was negatively mentioned in the article."},
                    "suspicious_activity": {"type": "boolean", "description": "Indicates if the person is involved in any suspicious activities."},
                    "suspicious_gifts_and_other": {"type": "boolean", "description": "Indicates if the article mentions suspicious gifts or other unusual financial behaviors."},
                    "finished_investigation": {"type": "boolean", "description": "Indicates if the investigation mentioned in the article has been concluded."}
                },
                "required": ["negative_mentions", "suspicious_activity", "suspicious_gifts_and_other", "finished_investigation"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

    prompt = dedent(f"""
    Analyze the following article content and determine whether the specified person is involved in specific activities.
    Focus on the person named "{person_name}" and provide the results in JSON format that adheres to the schema below.

    Schema:
    - negative_mentions: Indicates if the person was negatively mentioned in the article.
    - suspicious_activity: Indicates if the person is involved in any suspicious activities.
    - suspicious_gifts_and_other: Indicates if the article mentions suspicious gifts or other unusual financial behaviors.
    - finished_investigation: Indicates if the investigation mentioned in the article has been concluded.

    Article Content:
    {article["content"]}
    """)
    model = "gpt-4o-mini"

    def get_response(prompt, model, json_schema, client):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts information following a strict JSON schema."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            response_format = json_schema
        )
        event = response.choices[0].message
        return json.loads(event.content)

    return get_response(prompt, model, json_schema, client)
