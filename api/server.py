import time
import asyncio
import logging
import gradio as gr
from fastapi import FastAPI, BackgroundTasks, Request
from prometheus_fastapi_instrumentator import Instrumentator
from langchain_groq import ChatGroq
from core.config import settings
from api.memory_manager import AsyncRedisSessionManager

from tools.context_presence_judge import ContextPresenceJudgeTool
from tools.web_search_tool import WebSearchTool
from tools.context_relevance_checker import ContextRelevanceCheckerTool
from tools.context_splitter import ContextSplitterTool
from agent.agent_runner import ContextAwareAgentManager

logger = logging.getLogger(__name__)

app = FastAPI(title="Context-Aware Enterprise API")
Instrumentator().instrument(app).expose(app)
session_manager = AsyncRedisSessionManager()

llm = ChatGroq(temperature=0, model_name=settings.MODEL_NAME, api_key=settings.GROQ_API_KEY, streaming=True)
tools = [ContextPresenceJudgeTool(llm=llm), WebSearchTool(), ContextRelevanceCheckerTool(llm=llm), ContextSplitterTool(llm=llm)]
agent_executor = ContextAwareAgentManager(llm=llm, tools=tools).build_agent()

@app.on_event("startup")
async def startup_event():
    await session_manager.connect()

async def chat_stream_generator(message: str, history: list, request: gr.Request):
    "The live streaming generator that Gradio will consume"
    session_id = request.session_hash if request else "default_session"
    
    chat_history = await session_manager.get_history(session_id)
    
    try:
        result = await asyncio.to_thread(
            agent_executor.invoke, 
            {"input": message, "chat_history": chat_history}
        )
        final_answer = result.get("output", "Error generating response.")
        
        await session_manager.add_turn(session_id, message, final_answer)
        
        background_tasks = BackgroundTasks()
        background_tasks.add_task(session_manager.background_summarize, session_id, llm)
        
        streamed_response = ""
        for char in final_answer:
            streamed_response += char
            await asyncio.sleep(0.01) 
            yield streamed_response 
            
    except Exception as e:
        logger.error(f"Agent stream error: {e}")
        yield " An error occurred while processing your request."