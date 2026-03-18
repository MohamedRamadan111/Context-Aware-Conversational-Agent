import logging
import gradio as gr
from typing import Callable

logger = logging.getLogger(__name__)

# Custom CSS for a professional, enterprise-grade UI
custom_css = """
.gradio-container { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.message-row { margin-bottom: 20px !important; }
.user { background-color: #e6f7ff !important; border-radius: 15px 15px 0 15px !important; }
.bot { background-color: #f6f6f6 !important; border-radius: 15px 15px 15px 0 !important; }
"""

def build_ui(chat_function: Callable) -> gr.ChatInterface:
    """
    Builds and returns the Gradio ChatInterface.
    We directly pass the backend streaming function to Gradio.
    """
    logger.info("Initializing Gradio UI components...")

    demo = gr.ChatInterface(
        fn=chat_function, # We pass the backend generator directly here
        title="Context-Aware Enterprise Agent",
        description="Powered by FastAPI, Async Redis Memory, and Sustainable Computing.",
        css=custom_css,
        theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"),
        chatbot=gr.Chatbot(
            avatar_images=["👤", "🤖"],
            bubble_full_width=False
        )
    )

    return demo