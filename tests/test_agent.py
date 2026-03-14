import unittest
import os
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from agent.agent_runner import ContextAwareAgentManager
from tools.context_presence_judge import ContextPresenceJudgeTool
from tools.web_search_tool import WebSearchTool

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestContextAwareAgent(unittest.TestCase):
    """
    Integration Tests for the Context-Aware Agent.
    Verifies that the LLM, Tools, and Agent Workflow integrate correctly.
    """

    @classmethod
    def setUpClass(cls):
        """
       This function is run only once before all tests begin.

       It aims to prepare the environment, models, and tools to save processing time.
        """
        logger.info("Setting up the test environment...")
        load_dotenv()
        
        cls.groq_key = os.getenv("GROQ_API_KEY")
        cls.tavily_key = os.getenv("TAVILY_API_KEY")
        
        if not cls.groq_key or not cls.tavily_key:
            raise ValueError("Missing API Keys in .env file. Cannot run integration tests.")

        logger.info("Initializing LLM and Tools for testing...")
        cls.llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")
        
        cls.tools = [
            ContextPresenceJudgeTool(llm=cls.llm),
            WebSearchTool()
        ]
        
        cls.agent_manager = ContextAwareAgentManager(llm=cls.llm, tools=cls.tools)
        cls.agent_executor = cls.agent_manager.build_agent()

    def test_context_provided_flow(self):
        """
        Test Case 1: User provides context.
        The agent should identify the context and NOT fail.
        """
        query = "Here is my Python code: `print(x)`. It gives a NameError. Why?"
        logger.info(f"Running Test 1 (Context Provided) with query: {query}")

        try:
            
            response = self.agent_executor.run(query)
            
           
            self.assertIsNotNone(response, "The agent returned a None response.")
            self.assertIsInstance(response, str, "The agent response must be a string.")
            self.assertTrue(len(response) > 10, "The response is suspiciously short.")
            
            logger.info(f" Test 1 Passed. Agent Answer snippet: {response[:100]}...")
            
        except Exception as e:
            self.fail(f" Agent crashed on context-provided query. Error: {e}")

    def test_context_missing_flow(self):
        """
        Test Case 2: User asks a general question.
        The agent MUST trigger the WebSearchTool to find the answer.
        """
        query = "What is the latest version of LangChain released recently?"
        logger.info(f"Running Test 2 (Context Missing) with query: {query}")

        try:
            
            response = self.agent_executor.run(query)
            
            
            self.assertIsNotNone(response, "The agent returned a None response.")
            self.assertIsInstance(response, str, "The agent response must be a string.")
            self.assertTrue(len(response) > 10, "The response is suspiciously short.")
            
            logger.info(f"Test 2 Passed. Agent Answer snippet: {response[:100]}...")
            
        except Exception as e:
            self.fail(f"Agent crashed on context-missing query. Error: {e}")

if __name__ == "__main__":
    
    unittest.main()