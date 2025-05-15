from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from fastapi import FastAPI
from pydantic import BaseModel
import json
import time
from json_repair import repair_json

class CyberEntityExtractor:
    _instance = None  # Singleton instance

    def __init__(self):
        if CyberEntityExtractor._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            # Initialize model and prompt template
            self.llm = ChatOllama(model="mistral", temperature=0)
            self.prompt = ChatPromptTemplate.from_template(
                """
                You are a cybersecurity assistant. Extract the following types of entities from the text:
                - Persons
                - Organizations
                - IP Addresses
                - URLs
                - Dates
                - Vulnerabilities (e.g., CVEs)

                Respond in the following JSON format:
                {{
                  "Persons": [],
                  "Organizations": [],
                  "IP_Addresses": [],
                  "URLs": [],
                  "Dates": [],
                  "Vulnerabilities": []
                }}

                Text:
                {text}
                """
            )
            CyberEntityExtractor._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CyberEntityExtractor()
        return cls._instance

    def extract(self, text: str) -> str:
        formatted_prompt = self.prompt.format_messages(text=text)
        response = self.llm.invoke(formatted_prompt)
        return response.content
    



app = FastAPI()

# Pydantic input model
class EntityRequest(BaseModel):
    text: str

# Endpoint
@app.post("/extract_entities")
async def extract_entities(request: EntityRequest):
    start_time = time.time()
    model = CyberEntityExtractor.get_instance()
    result = model.extract(request.text)
    good_json_string = repair_json(result)
    end_time = time.time()
    inference_time = end_time - start_time
    print(f"[Inference Time] --> {inference_time:.3f} seconds")
    parsed_entities = json.loads(good_json_string)
    return {"entities": parsed_entities}   