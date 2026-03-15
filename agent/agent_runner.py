import logging
from typing import List, Optional
import os
from langchain.agents import initialize_agent, AgentType, AgentExecutor

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
            self.agent_executor = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                # agent=AgentType.REACT_DESCRIPTION,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=self._handle_parsing_error,
                max_iterations=5, # Protection against infinite loops
                early_stopping_method="generate"
                agent_kwargs={'prefix': custom_prompt}
            )
            logger.info("Agent built successfully.")
            return self.agent_executor
        except Exception as e:
            logger.critical(f"Failed to build agent: {e}")
            raise