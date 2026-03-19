import os
from typing import Any, Optional
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
# from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

class ContextSplitterInput(BaseModel):
    query: str = Field(..., description="The relevant user message to be split into background context and the core question.")

class ContextSplitterTool(BaseTool):  
    name:str="ContextSplitter"
    args_schema: type[BaseModel] = ContextSplitterInput
    description: str = "Separates background info from the question. ONLY use if ContextRelevanceChecker says 'relevant'."

    llm: Optional[ChatGroq] = None
    def _get_prompt(self) -> str:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            prompt_path = os.path.join(current_dir, "..", "prompts", "context_splitter_prompt.txt")
            
            with open(prompt_path, "r", encoding="utf-8") as file:
                system_prompt = file.read().strip()
                return system_prompt
                
        except FileNotFoundError:
            print("Error: context_splitter_prompt.txt was not found.")
            return ""
        
    
    def _run(self, query: str) -> str:
        try:
            system_prompt = self._get_prompt()
            if not system_prompt:
                return query
            formatted_prompt = system_prompt.replace("{input}", query)
            
            response = self.llm.invoke(formatted_prompt)
            
            result = response.content.strip()
        
            return result
                
        except Exception as e:
            print(f"Context splitter API Error: {e}")
            return "context_missing"
        


