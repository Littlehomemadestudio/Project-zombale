# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from .request.http import HTTPClient
from .handlers import BaseHandler
from .update import Update
from .message import Message
from .callbackquery import CallbackQuery

logger = logging.getLogger(__name__)

class Bot:
    """Main Bot class for Bale API"""
    
    def __init__(self, token: str):
        self.token = token
        self.http = HTTPClient(token)
        self.handlers: List[BaseHandler] = []
        self.running = False
        self.user: Optional[Dict] = None
        
    async def get_me(self) -> Dict[str, Any]:
        """Get bot information"""
        return await self.http.get_me()
    
    async def send_message(self, chat_id: Union[str, int], text: str, 
                          reply_markup: Optional[Any] = None,
                          parse_mode: str = "Markdown") -> Message:
        """Send a text message"""
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        if reply_markup:
            data["reply_markup"] = reply_markup.to_dict() if hasattr(reply_markup, 'to_dict') else reply_markup
            
        response = await self.http.send_message(data)
        return Message.from_dict(response["result"])
    
    async def send_photo(self, chat_id: Union[str, int], photo: Any, 
                        caption: str = "", reply_markup: Optional[Any] = None) -> Message:
        """Send a photo"""
        data = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption
        }
        
        if reply_markup:
            data["reply_markup"] = reply_markup.to_dict() if hasattr(reply_markup, 'to_dict') else reply_markup
            
        response = await self.http.send_photo(data)
        return Message.from_dict(response["result"])
    
    async def send_document(self, chat_id: Union[str, int], document: Any, 
                           caption: str = "") -> Message:
        """Send a document"""
        data = {
            "chat_id": chat_id,
            "document": document,
            "caption": caption
        }
        
        response = await self.http.send_document(data)
        return Message.from_dict(response["result"])
    
    async def edit_message_text(self, chat_id: Union[str, int], message_id: int, 
                               text: str, reply_markup: Optional[Any] = None) -> Message:
        """Edit message text"""
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
        
        if reply_markup:
            data["reply_markup"] = reply_markup.to_dict() if hasattr(reply_markup, 'to_dict') else reply_markup
            
        response = await self.http.edit_message_text(data)
        return Message.from_dict(response["result"])
    
    async def answer_callback_query(self, callback_query_id: str, text: str = "", 
                                   show_alert: bool = False) -> bool:
        """Answer a callback query"""
        data = {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert
        }
        
        response = await self.http.answer_callback_query(data)
        return response.get("ok", False)
    
    async def get_chat_member(self, chat_id: Union[str, int], user_id: Union[str, int]) -> Dict[str, Any]:
        """Get chat member information"""
        data = {
            "chat_id": chat_id,
            "user_id": user_id
        }
        
        response = await self.http.get_chat_member(data)
        return response["result"]
    
    def handle(self, handler: BaseHandler):
        """Add a handler to the bot"""
        self.handlers.append(handler)
        return handler
    
    def listen(self, event: str):
        """Decorator for event listeners"""
        def decorator(func: Callable):
            # Store event listener
            setattr(self, f"_{event}_handler", func)
            return func
        return decorator
    
    async def process_update(self, update_data: Dict[str, Any]):
        """Process incoming update"""
        try:
            update = Update.from_dict(update_data)
            
            for handler in self.handlers:
                if await handler.check(update):
                    await handler.handle(update)
                    break
                    
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    async def start_polling(self, update_handler: Optional[Callable] = None, 
                           allowed_updates: Optional[List[str]] = None):
        """Start polling for updates"""
        logger.info("Starting bot polling...")
        self.running = True
        
        # Get bot info
        self.user = await self.get_me()
        logger.info(f"Bot started: {self.user.get('first_name', 'Unknown')}")
        
        # Start polling loop
        offset = 0
        while self.running:
            try:
                updates = await self.http.get_updates(offset=offset, allowed_updates=allowed_updates)
                
                for update_data in updates:
                    if update_handler:
                        await update_handler(update_data)
                    else:
                        await self.process_update(update_data)
                    
                    offset = update_data["update_id"] + 1
                
                await asyncio.sleep(1)  # Polling interval
                
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def stop_polling(self):
        """Stop polling"""
        logger.info("Stopping bot polling...")
        self.running = False
    
    def run(self):
        """Run the bot (blocking)"""
        asyncio.run(self._run())
    
    async def _run(self):
        """Internal run method"""
        try:
            await self.start_polling()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            await self.stop_polling()