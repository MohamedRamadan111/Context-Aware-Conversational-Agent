import sys
import logging
import uvicorn
import gradio as gr

from ui.app import build_ui

from api.server import app as fastapi_app
from api.server import chat_stream_generator

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main() -> None:
    """
    The application's main entry point (V3 - Enterprise Architecture).
    It mounts the Gradio UI onto the FastAPI backend and launches the ASGI server.
    """
   
    logger.info(" Launching V3: FastAPI + Gradio + Async Memory...")
    
    try:
        logger.info("Initializing Gradio User Interface...")

        demo = build_ui(chat_function=chat_stream_generator)
        
        logger.info("Mounting Gradio UI onto FastAPI server...")
        app = gr.mount_gradio_app(fastapi_app, demo, path="/")
        
        logger.info("System is ready. Launching Uvicorn server on http://0.0.0.0:7860")
        uvicorn.run(app, host="0.0.0.0", port=7860)
        
    except Exception as e:
        logger.critical(f"Fatal error during system startup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()