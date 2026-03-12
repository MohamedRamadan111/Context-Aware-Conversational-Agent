import os
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

class ContextPresenceInput(BaseModel):
    query: str = Field(..., description="The user's raw message to evaluate for context.")    

class ContextPresenceJudgeTool(BaseTool):
    name:str="ContextPresenceJudge"
    args_schema: type[BaseModel] = ContextPresenceInput
    description: str = "Use this tool to determine whether the user gave enough background or context in their message before answering."
#    __init__ is just for optimization but the pydantic will generate one by itself is there is no __init__


    def _run(self, query: str) -> str:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            prompt_path = os.path.join(current_dir, "..", "prompts", "context_judge_prompt.txt")
            
            with open(prompt_path, "r", encoding="utf-8") as file:
                system_prompt = file.read().strip()
                
        except FileNotFoundError:
            print("Error: context_judge_prompt.txt was not found.")
            return "context_missing"

        try:
            github_token = os.getenv("github_token") 
            
            llm = ChatOpenAI(
                model="meta/Llama-4-Scout-17B-16E-Instruct",
                api_key=github_token,
                base_url="https://models.github.ai/inference",
                temperature=0.0, 
                max_tokens=2048,
                model_kwargs={"top_p": 0.1}
            )
            formatted_prompt = system_prompt.replace("{input}", query)
            
            response = llm.invoke(formatted_prompt)
            
            result = response.content.lower().strip()
            
            if result in ["context_provided", "context_missing"]:
                return result
            else:
                print(f"Warning: LLM returned unexpected format: {result}")
                return "context_missing"
                
        except Exception as e:
            print(f"Context Judge API Error: {e}")
            return "context_missing"
        



