"""
Bale API wrapper for BalletBot: Outbreak Dominion
Handles Bale messenger integration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from bale import Bot, Update, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

@dataclass
class User:
    """User data structure"""
    id: str
    username: str
    first_name: str
    last_name: Optional[str] = None
    is_bot: bool = False

class BaleAPI:
    """Bale API wrapper for the bot"""
    
    def __init__(self, token: str):
        self.bot = Bot(token)
        self.command_handlers: Dict[str, Callable] = {}
        self.message_handlers: List[Callable] = []
        self.callback_handlers: Dict[str, Callable] = {}
        self.running = False
        
    def command(self, command: str):
        """Decorator for command handlers"""
        def decorator(func):
            self.command_handlers[command] = func
            return func
        return decorator
    
    def message_handler(self, func):
        """Decorator for message handlers"""
        self.message_handlers.append(func)
        return func
    
    def callback_handler(self, callback_data: str):
        """Decorator for callback handlers"""
        def decorator(func):
            self.callback_handlers[callback_data] = func
            return func
        return decorator
    
    async def send_message(self, chat_id: str, text: str, 
                          reply_markup: Optional[InlineKeyboardMarkup] = None,
                          parse_mode: str = "Markdown") -> bool:
        """Send a text message"""
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False
    
    async def send_photo(self, chat_id: str, photo_path: str, 
                        caption: str = "", 
                        reply_markup: Optional[InlineKeyboardMarkup] = None) -> bool:
        """Send a photo"""
        try:
            with open(photo_path, 'rb') as photo:
                await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    reply_markup=reply_markup
                )
            return True
        except Exception as e:
            logger.error(f"Failed to send photo to {chat_id}: {e}")
            return False
    
    async def send_document(self, chat_id: str, document_path: str, 
                           caption: str = "") -> bool:
        """Send a document"""
        try:
            with open(document_path, 'rb') as doc:
                await self.bot.send_document(
                    chat_id=chat_id,
                    document=doc,
                    caption=caption
                )
            return True
        except Exception as e:
            logger.error(f"Failed to send document to {chat_id}: {e}")
            return False
    
    async def edit_message_text(self, chat_id: str, message_id: int, text: str,
                               reply_markup: Optional[InlineKeyboardMarkup] = None) -> bool:
        """Edit message text"""
        try:
            await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            logger.error(f"Failed to edit message in {chat_id}: {e}")
            return False
    
    async def answer_callback_query(self, callback_query_id: str, text: str = "", 
                                   show_alert: bool = False) -> bool:
        """Answer a callback query"""
        try:
            await self.bot.answer_callback_query(
                callback_query_id=callback_query_id,
                text=text,
                show_alert=show_alert
            )
            return True
        except Exception as e:
            logger.error(f"Failed to answer callback query: {e}")
            return False
    
    async def is_admin(self, chat_id: str, user_id: str) -> bool:
        """Check if user is admin in chat"""
        try:
            chat_member = await self.bot.get_chat_member(chat_id, user_id)
            return chat_member.status in ['creator', 'administrator']
        except Exception as e:
            logger.error(f"Failed to check admin status: {e}")
            return False
    
    async def get_chat_member(self, chat_id: str, user_id: str) -> Optional[Dict]:
        """Get chat member information"""
        try:
            return await self.bot.get_chat_member(chat_id, user_id)
        except Exception as e:
            logger.error(f"Failed to get chat member: {e}")
            return None
    
    def create_inline_keyboard(self, buttons: List[List[Dict[str, str]]]) -> InlineKeyboardMarkup:
        """Create inline keyboard markup"""
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button in row:
                keyboard_row.append(InlineKeyboardButton(
                    text=button['text'],
                    callback_data=button['callback_data']
                ))
            keyboard.append(keyboard_row)
        return InlineKeyboardMarkup(keyboard)
    
    async def process_update(self, update: Update):
        """Process incoming update"""
        try:
            if update.message:
                await self._process_message(update.message)
            elif update.callback_query:
                await self._process_callback_query(update.callback_query)
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    async def _process_message(self, message: Message):
        """Process incoming message"""
        if not message.text:
            return
        
        text = message.text.strip()
        chat_id = str(message.chat.id)
        user_id = str(message.from_user.id)
        
        # Check for commands
        if text.startswith('/'):
            command_parts = text.split(' ', 1)
            command = command_parts[0]
            args = command_parts[1] if len(command_parts) > 1 else ""
            
            if command in self.command_handlers:
                try:
                    await self.command_handlers[command](message, args)
                except Exception as e:
                    logger.error(f"Error in command handler {command}: {e}")
                    await self.send_message(chat_id, "❌ An error occurred processing your command.")
            else:
                # Try message handlers
                for handler in self.message_handlers:
                    try:
                        await handler(message)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
        else:
            # Process as regular message
            for handler in self.message_handlers:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")
    
    async def _process_callback_query(self, callback_query: CallbackQuery):
        """Process callback query"""
        data = callback_query.data
        chat_id = str(callback_query.message.chat.id)
        user_id = str(callback_query.from_user.id)
        
        if data in self.callback_handlers:
            try:
                await self.callback_handlers[data](callback_query)
            except Exception as e:
                logger.error(f"Error in callback handler {data}: {e}")
                await self.answer_callback_query(callback_query.id, "❌ An error occurred.")
    
    async def start_polling(self):
        """Start polling for updates"""
        logger.info("Starting Bale bot polling...")
        self.running = True
        
        try:
            await self.bot.start_polling(
                update_handler=self.process_update,
                allowed_updates=['message', 'callback_query']
            )
        except Exception as e:
            logger.error(f"Error in polling: {e}")
            raise
    
    async def stop_polling(self):
        """Stop polling"""
        logger.info("Stopping Bale bot polling...")
        self.running = False
        await self.bot.stop_polling()
    
    def get_user_info(self, user) -> User:
        """Extract user information from Bale user object"""
        return User(
            id=str(user.id),
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name,
            is_bot=user.is_bot
        )