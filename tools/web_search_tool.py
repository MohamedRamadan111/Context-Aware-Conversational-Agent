import os
import requests
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()

class WebSearchInput(BaseModel):
    query: str = Field(..., description="The specific search query to look up on the internet.")




class WebSearchTool(BaseTool):
    name: str = "WebSearchTool"
    description: str = "Use this tool to search the internet for external information ONLY when the user's context is missing."
    args_schema: type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:
        try:
            TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") 
            if not TAVILY_API_KEY:
                return "Error: TAVILY API key is missing."
            
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": TAVILY_API_KEY,
                "query": query
            }
            
            response = requests.post(url, json=payload, timeout=50)
            
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                return "No relevant information found on the web."
            else:
                return results[0].get("content", "No content found in result.")
            
        except requests.exceptions.Timeout:
            print("Warning: Tavily search timed out.")
            return "Error: Search service timed out."
            
        except requests.exceptions.HTTPError as e:
            print(f"Tavily HTTP Error: {e}")
            return "context_missing"
            
        except Exception as e:
            print(f"TAVILY API  Error: {e}")
            return "context_missing"