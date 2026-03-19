import os
from typing import Any, Optional
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
# from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

class ContextRelevanceInput(BaseModel):
    query: str = Field(..., description="The user's message containing both the background context and the question to be evaluated for relevance.")  


class ContextRelevanceCheckerTool(BaseTool):  
    name:str="ContextRelevanceChecker"
    args_schema: type[BaseModel] = ContextRelevanceInput
    description: str = "Checks if the context matches the question. ONLY use if ContextPresenceJudge says 'context_provided'."

    llm: Optional[ChatGroq] = None
    def _get_prompt(self) -> str:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            prompt_path = os.path.join(current_dir, "..", "prompts", "context_relevance_prompt.txt")
            
            with open(prompt_path, "r", encoding="utf-8") as file:
                system_prompt = file.read().strip()
                return system_prompt
                
        except FileNotFoundError:
            print("Error: context_relevance_prompt.txt was not found.")
            return "irrelevant"
        
    
    def _run(self, query: str) -> str:
        try:
            system_prompt = self._get_prompt()
            formatted_prompt = system_prompt.replace("{input}", query)
            
            response = self.llm.invoke(formatted_prompt)
            
            result = response.content.lower().strip()
            
            if "relevant" in result and result != "irrelevant":
                return "relevant"
            return "irrelevant"
                
        except Exception as e:
            print(f"Relevance Checker Error: {e}")
            return "irrelevant"
        


