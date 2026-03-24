import logging
import gradio as gr
from typing import Callable

logger = logging.getLogger(__name__)

# Custom CSS for a full-screen, ultra-modern "cooler" look
custom_css = """
/* Expand container to fit screen perfectly */
.gradio-container {
    max-width: 1400px !important;
}

/* Gradient text for the main title to make it pop */
.title-text {
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900;
    font-size: 2.5em;
}

/* Style the subtitle */
.subtitle-text {
    color: #8892b0;
    font-size: 1.1em;
}

/* Add a subtle glow/glassmorphism to the chat window */
.contain {
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}
"""

def build_ui(chat_function: Callable) -> gr.Blocks:
    """
    Builds and returns the Gradio UI using Blocks for a native-app feel.
    """
    logger.info("Initializing Gradio UI components...")

    # Switch to a sleeker Ocean theme with high contrast dark mode
    premium_theme = gr.themes.Ocean(
        primary_hue="sky",
        secondary_hue="blue",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    ).set(
        body_background_fill="*neutral_950",
        block_background_fill="*neutral_900",
        block_border_width="1px",
        block_border_color="*neutral_800",
        button_primary_background_fill="*primary_600",
        button_primary_background_fill_hover="*primary_500",
        border_color_primary="*primary_600",
    )

    # fill_height=True stretches the app to fit the window perfectly!
    with gr.Blocks(theme=premium_theme, css=custom_css, fill_height=True) as demo:
        
        # Ultra-modern Header
        gr.Markdown("<h1 class='title-text' style='text-align: center; margin-bottom: 5px;'>Context-Aware Enterprise Agent ⚡</h1>")
        gr.Markdown("<p class='subtitle-text' style='text-align: center; margin-top: 0;'><b>Powered by FastAPI, Async Redis Memory, and LLaMA 3.3</b><br> </p>")
        
        # The Chat Interface
        gr.ChatInterface(
            fn=chat_function, 
            chatbot=gr.Chatbot(
                show_label=False,
                scale=1, # Replaces fixed height, stretches dynamically to fit screen
                avatar_images=[
                    "https://api.dicebear.com/7.x/avataaars/svg?seed=MW&backgroundColor=b6e3f4", # User Avatar
                    "https://api.dicebear.com/7.x/bottts/svg?seed=Agent&backgroundColor=1e293b"  # AI Avatar (Darker BG to match theme)
                ]
            ),
            textbox=gr.Textbox(
                placeholder="Ask a question, or paste some code here...",
                container=False,
                scale=7
            ),
            examples=[
                "What is the latest version of LangChain released recently?",
                "Here is a recipe for chicken: 1 cup rice, 2 chicken breasts. How do I fix a NameError in Python?"
            ],
        )

    return demo