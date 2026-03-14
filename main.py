import sys
import logging
from tkinter.ttk import Entry
from core.config import settings
from langchain_groq import ChatGroq

from tools.context_presence_judge import ContextPresenceJudgeTool
from tools.web_search_tool import WebSearchTool
from agent.agent_runner import ContextAwareAgentManager
from ui.app import build_ui

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main() -> None:
    
    """

    The application's main entry point.

    It configures settings, builds tools, compiles the agent, and launches the interface.

    """
    
    logger.info(" Starting Context-Aware Agent System...")
    
    try:
        logger.info("Validating environment configurations...")
        settings.validate()
        
        logger.info(f"Initializing LLM ({settings.MODEL_NAME})...")
        llm = ChatGroq(
            temperature=0, 
            model_name=settings.MODEL_NAME,
            api_key=settings.GROQ_API_KEY
        )
        
        
        logger.info("Loading AI Tools...")
        tools = [
            ContextPresenceJudgeTool(llm=llm),
            WebSearchTool()
        ]
        
        
        logger.info("Building the Agent Engine...")
        agent_manager = ContextAwareAgentManager(llm=llm, tools=tools)
        agent_executor = agent_manager.build_agent()
        
        
        logger.info("Initializing Gradio User Interface...")
        demo = build_ui(agent_executor=agent_executor)
        
        logger.info("System is ready. Launching server on http://127.0.0.1:7860")
        
        demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
        
    except Exception as e:
        
        logger.critical(f"Fatal error during system startup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()