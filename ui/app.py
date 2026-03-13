import logging
import gradio as gr
from typing import Any

logger = logging.getLogger(__name__)

def build_ui(agent_executor: Any) -> gr.ChatInterface:
    """Building the user interface and wrapping the agent call with error handling."""
    
    def chat_wrapper(message: str, history: list) -> str:
        try:
            logger.info(f"User asking: {message}")
            response = agent_executor.run(message)
            return response
        except Exception as e:
            logger.error(f"UI Error during agent execution: {str(e)}")
            return " Sorry, an internal error occurred while processing your request."

    demo = gr.ChatInterface(
        fn=chat_wrapper,
        title=" Context-Aware AI Agent",
        description="A smart agent designed with advanced software engineering principles.",
        theme=gr.themes.Soft()
    )
    return demo