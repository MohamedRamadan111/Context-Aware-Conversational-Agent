import logging
import gradio as gr
from typing import Callable, Generator

logger = logging.getLogger(__name__)

custom_css = """
.gradio-container { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.message-row { margin-bottom: 20px !important; }
.user { background-color: #e6f7ff !important; border-radius: 15px 15px 0 15px !important; }
.bot { background-color: #f6f6f6 !important; border-radius: 15px 15px 15px 0 !important; }
"""

def build_ui(chat_function: Callable) -> gr.ChatInterface:
    

    def chat_wrapper(message: str, history: list) -> Generator[str, None, None]:
        try:
            logger.info(f"User asking: {message}")

            for chunk in chat_function(message, history):
                yield chunk

        except Exception as e:
            logger.error(f"UI Error during agent execution: {str(e)}")
            yield "Sorry, an internal error occurred while processing your request."

    demo = gr.ChatInterface(
        fn=chat_wrapper,
        title="Context-Aware AI Assistant",
        description="Powered by Llama 3 & LangChain with Real-time Streaming and Memory.",
        css=custom_css,
        theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"),

        chatbot=gr.Chatbot(
            avatar_images=["👤", "🤖"],
            bubble_full_width=False
        )
    )

    return demo