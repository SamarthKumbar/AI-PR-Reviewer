
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
# openai.api_key = os.getenv("API_KEY")
# openai.api_base = "https://api.groq.com/openai/v1"


PROMPT_TEMPLATE = """
You are a senior software engineer reviewing a GitHub pull request. Here is the diff:

{diff}

Analyze the changes and return a review summary in this exact JSON format:

{{
  "files": [
    {{
      "name": "<filename>",
      "issues": [
        {{
          "type": "<style|bug|security|performance|docs|other>",
          "line": <line_number>,
          "description": "<brief explanation>",
          "suggestion": "<actionable fix>"
        }}
      ]
    }}
  ],
  "summary": {{
    "total_files": <int>,
    "total_issues": <int>,
    "critical_issues": <int>
  }}
}}

Only return valid JSON. Do not include markdown or explanations.
"""

def summarize_and_review_diff(diff):
    """Analyzes a code diff using an LLM and returns a structured review."""
    try:
        response =  client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": PROMPT_TEMPLATE.format(diff=diff[:8000])
            }],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        output = response.choices[0].message.content
        if not output:
            return None, "Model returned an empty response."

        parsed = json.loads(output)
        return parsed, None
    except Exception as e:
        return None, f"An error occurred during AI analysis: {e}"