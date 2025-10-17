"""
Bale API wrapper for BalletBot: Outbreak Dominion
Provides a thin wrapper around Bale API with mock support for development
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class BaleAPI:
    """Bale API wrapper with mock support for development"""
    
    def __init__(self, token: str = None, mock_mode: bool = True):
        self.token = token
        self.mock_mode = mock_mode
        self.bot = None
        
        if not mock_mode and token:
            try:
                import bale
                self.bot = bale.Bot(token=token)
                logger.info("Bale bot initialized successfully")
            except ImportError:
                logger.error("Bale library not installed. Using mock mode.")
                self.mock_mode = True
        else:
            logger.info("Running in mock mode")
    
    async def send_message(self, chat_id: str, text: str, **kwargs) -> bool:
        """Send message to group chat"""
        if self.mock_mode:
            logger.info(f"MOCK SEND MESSAGE to {chat_id}: {text}")
            return True
        
        try:
            await self.bot.send_message(chat_id, text, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    async def send_photo(self, chat_id: str, photo_path: str, caption: str = None) -> bool:
        """Send photo to group chat"""
        if self.mock_mode:
            logger.info(f"MOCK SEND PHOTO to {chat_id}: {photo_path} (caption: {caption})")
            return True
        
        try:
            with open(photo_path, 'rb') as photo:
                await self.bot.send_photo(chat_id, photo, caption=caption)
            return True
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            return False
    
    async def send_private_message(self, user_id: str, text: str, **kwargs) -> bool:
        """Send private message to user"""
        if self.mock_mode:
            logger.info(f"MOCK SEND PM to {user_id}: {text}")
            return True
        
        try:
            await self.bot.send_private_message(user_id, text, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Failed to send private message: {e}")
            return False
    
    def on_command(self, command: str):
        """Decorator for command handlers"""
        def decorator(func):
            if self.mock_mode:
                logger.info(f"MOCK COMMAND REGISTERED: {command}")
                return func
            else:
                return self.bot.command(command)(func)
        return decorator
    
    def on_message(self):
        """Decorator for message handlers"""
        def decorator(func):
            if self.mock_mode:
                logger.info("MOCK MESSAGE HANDLER REGISTERED")
                return func
            else:
                return self.bot.message(func)
        return decorator
    
    async def get_chat_member(self, chat_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get chat member information"""
        if self.mock_mode:
            return {
                "user": {"id": user_id, "username": f"user_{user_id}"},
                "status": "member"
            }
        
        try:
            return await self.bot.get_chat_member(chat_id, user_id)
        except Exception as e:
            logger.error(f"Failed to get chat member: {e}")
            return None
    
    async def get_chat_administrators(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get chat administrators"""
        if self.mock_mode:
            return [{"user": {"id": "admin1", "username": "admin"}}]
        
        try:
            return await self.bot.get_chat_administrators(chat_id)
        except Exception as e:
            logger.error(f"Failed to get chat administrators: {e}")
            return []
    
    async def start_polling(self):
        """Start the bot polling"""
        if self.mock_mode:
            logger.info("MOCK BOT: Polling started (mock mode)")
            return
        
        try:
            await self.bot.start_polling()
        except Exception as e:
            logger.error(f"Failed to start polling: {e}")

# Global API instance
api = BaleAPI(mock_mode=True)  # Set to False when ready to use real Bale API