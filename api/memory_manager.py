import json
import logging
import os
import redis.asyncio as redis
from dotenv import load_dotenv


logger = logging.getLogger(__name__)

class AsyncRedisSessionManager:
    def __init__(self, redis_url=None):
        self.redis_url = redis_url or os.getenv("redisURL")
        self.client = None

    async def connect(self):
        """Asynchronous connection setup (must be called when FastAPI starts)"""
        if not self.client:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            try:
                await self.client.ping()
                logger.info("Successfully connected to Async Redis.")
            except Exception as e:
                logger.error(f"Async Redis connection failed: {e}")
                self.client = None

    async def add_turn(self, session_id: str, user_msg: str, ai_msg: str):
        """Adding new messages to the sliding window"""
        if not self.client: 
            return

        messages_key = f"session:{session_id}:messages"
        
        
        user_data = json.dumps({"role": "user", "content": user_msg})
        ai_data = json.dumps({"role": "assistant", "content": ai_msg})
        
        
        await self.client.rpush(messages_key, user_data, ai_data)
        
        
        await self.client.expire(messages_key, 86400)
        await self.client.expire(f"session:{session_id}:summary", 86400)

    async def get_history(self, session_id: str) -> str:
        """Fetching the integrated history (previous summary + latest messages)"""
        if not self.client: 
            return "No previous history."
        
        summary_key = f"session:{session_id}:summary"
        messages_key = f"session:{session_id}:messages"
        
        
        summary = await self.client.get(summary_key)
        
        raw_messages = await self.client.lrange(messages_key, 0, -1)
        
        history_text = ""
        if summary:
            history_text += f"[System Memory Summary]: {summary}\n\n"
        
        
        for msg_str in raw_messages:
            try:
                msg = json.loads(msg_str)
                role = "User" if msg["role"] == "user" else "AI"
                history_text += f"{role}: {msg['content']}\n"
            except json.JSONDecodeError:
                continue
            
        return history_text.strip() if history_text else "No previous history."

    async def background_summarize(self, session_id: str, llm):
        """
        Background Task for compressing old messages and trimming the list (LTRIM).
        """
        if not self.client: 
            return
        
        messages_key = f"session:{session_id}:messages"
        summary_key = f"session:{session_id}:summary"
        
        
        msg_count = await self.client.llen(messages_key)
        
        
        if msg_count > 10:
            
            old_messages_raw = await self.client.lrange(messages_key, 0, msg_count - 11)
            if not old_messages_raw: 
                return
            
            old_history = ""
            for msg_str in old_messages_raw:
                try:
                    msg = json.loads(msg_str)
                    old_history += f"{msg['role']}: {msg['content']}\n"
                except json.JSONDecodeError:
                    continue
            
            
            current_summary = await self.client.get(summary_key) or "No previous summary."
            
            prompt = (
                f"Combine and summarize the following conversational context concisely.\n"
                f"Previous Summary: {current_summary}\n"
                f"New conversation to summarize:\n{old_history}"
            )
            
            try:
                
                summary_result = await llm.ainvoke(prompt)
                new_summary = summary_result.content
                
                
                await self.client.set(summary_key, new_summary)
                
                
                await self.client.ltrim(messages_key, -10, -1)
                
                logger.info(f"Successfully summarized memory and trimmed window for session {session_id}")
            except Exception as e:
                logger.error(f"Failed to summarize memory: {e}")