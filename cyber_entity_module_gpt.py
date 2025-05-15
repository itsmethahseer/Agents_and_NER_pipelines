from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import json
import re
import os
from dotenv import load_dotenv

load_dotenv(".env", override=True)

app = FastAPI()

# Define input structure
class QueryInput(BaseModel):
    query: str

# Effective Prompt Template for GPT-4o
PROMPT_TEMPLATE = """
You are an advanced cybersecurity assistant. Extract the following entities from the given query:
- Person (e.g., engineers, analysts, developers, security team)
- Host (e.g., Windows devices, Linux servers, laptops, database servers)
- Vulnerability (e.g., CVE-2023-9999, Log4j, SQL Injection, RCE vulnerabilities)

Query: "{query}"

Respond in JSON format:
{{
  "entities": {{
    "person": ["List of detected person entities"],
    "host": ["List of detected host entities"],
    "vulnerability": ["List of detected vulnerability entities"]
  }}
}}
Ensure the JSON is valid and parsable. Do not include any surrounding markdown formatting like backticks.
"""

client = openai.OpenAI(api_key="")
model_name = "gpt-4o"  # Specify the GPT-4o model


def run_gpt4o(prompt: str) -> str:
    """Send a prompt to the GPT-4o model and get the response."""
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed for cybersecurity entity extraction."},
                {"role": "user", "content": prompt},
            ],
        )
        # The response is a ChatCompletion object. Extract the content.
        response_text = response.choices[0].message.content
        return response_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running GPT-4o prompt: {e}")


@app.post("/extract-entities")
async def extract_entities(query_input: QueryInput):
    """
    Extracts entities from the given query using the GPT-4o model.

    Args:
        query_input (QueryInput): The input containing the query string.

    Returns:
        dict: A JSON object containing the extracted entities (person, host, vulnerability).

    Raises:
        HTTPException: If there is an error communicating with the GPT-4o model or parsing the response.
    """
    # Construct the prompt
    prompt = PROMPT_TEMPLATE.format(query=query_input.query)

    # Get the response from GPT-4o
    response_text = run_gpt4o(prompt)

    # Clean the response (GPT-4o is generally better at following instructions,
    # but we include this for robustness)
    cleaned_text = response_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[len("```json"):]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
    cleaned_text = cleaned_text.strip()

    # Attempt to load the cleaned text as JSON
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Problematic Response Text:\n{response_text}")
        raise HTTPException(status_code=500, detail=f"Error parsing GPT-4o response: {e}")