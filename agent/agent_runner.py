import logging
from typing import List, Optional

from langchain.agents import initialize_agent, AgentType, AgentExecutor

from langchain.tools import BaseTool
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

class ContextAwareAgentManager:
    def __init__(self, llm: ChatGroq, tools: List[BaseTool]):
        self.llm = llm
        self.tools = tools
        self.agent_executor: Optional[AgentExecutor] = None

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
            )
            logger.info("Agent built successfully.")
            return self.agent_executor
        except Exception as e:
            logger.critical(f"Failed to build agent: {e}")
            raise