from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import json
import re

app = FastAPI()

# Define input structure
class QueryInput(BaseModel):
    query: str

# Effective Prompt Template for Gemini 2.0 Flash
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
Never include backticks in your response.  The JSON should be valid and parsable.
"""

# Initialize Gemini 2.0 Flash
GOOGLE_API_KEY = ""  # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')  # Specify the Gemini Flash model


def run_gemini(prompt: str) -> str:
    """Send a prompt to the Gemini 2.0 Flash model and get the response."""
    try:
        response = model.generate_content(prompt)
        # The response is a `GenerateContentResponse` object.  Extract the text.
        response_text = response.text
        return response_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running Gemini prompt: {e}")



@app.post("/extract-entities")
async def extract_entities(query_input: QueryInput):
        """
        Extracts entities from the given query using the Gemini 2.0 Flash model.

        Args:
            query_input (QueryInput): The input containing the query string.

        Returns:
            dict: A JSON object containing the extracted entities (person, host, vulnerability).

        Raises:
            HTTPException: If there is an error communicating with the Gemini model or parsing the response.
        """
        # Construct the prompt
        prompt = PROMPT_TEMPLATE.format(query=query_input.query)

        
        # Get the response from Gemini 2.0 Flash
        response_text = run_gemini(prompt)
        cleaned_text = re.sub(r"^```(?:json\n)?", "", response_text)
        cleaned_text = re.sub(r"```$", "", cleaned_text).strip()

  # Remove double quotes from keys and string values
        cleaned_text = cleaned_text.replace('\\"', '"') # Unescape escaped double quotes
        return json.loads(cleaned_text)