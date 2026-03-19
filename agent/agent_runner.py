import logging
from typing import List, Optional
import os

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

class ContextAwareAgentManager:
    def __init__(self, llm: ChatGroq, tools: List[BaseTool]):
        self.llm = llm
        self.tools = tools
        self.agent_executor: Optional[AgentExecutor] = None

    def _load_custom_prompt(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(base_dir, "prompts", "agent_prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()

    def _handle_parsing_error(self, error: Exception) -> str:
        """Prevent the agent from crashing if the model makes a formatting error."""
        logger.warning(f"Parsing error caught: {error}")
        return "Observation: Invalid format. Please use Thought/Action/Action Input format."

    def build_agent(self) -> AgentExecutor:
        try:
            prompt_text = self._load_custom_prompt()
            
            # Your Week 2 fix: Manually format the tools
            tool_descriptions = "\n".join([f"{t.name}: {t.description}" for t in self.tools])
            tool_names = ", ".join([t.name for t in self.tools])
            
            # The teammate's Week 3 feature: added "chat_history"
            prompt = PromptTemplate(
                template=prompt_text,
                input_variables=["input", "agent_scratchpad", "chat_history"],
                partial_variables={
                    "tools": tool_descriptions,
                    "tool_names": tool_names
                }
            )

            agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )

            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=self._handle_parsing_error,
                max_iterations=5, 
                early_stopping_method="force"
            )
            
            logger.info("Agent built successfully.")
            return self.agent_executor
        except Exception as e:
            logger.critical(f"Failed to build agent: {e}")
            raise