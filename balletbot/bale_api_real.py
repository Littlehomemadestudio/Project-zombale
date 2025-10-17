"""
Real Bale API wrapper for BalletBot: Outbreak Dominion
Handles Bale messenger integration using the actual Bale API
"""

import asyncio
import logging
import aiohttp
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

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
    """Real Bale API wrapper for the bot"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://tapi.bale.ai/bot{token}"
        self.session: Optional[aiohttp.ClientSession] = None
        self.command_handlers: Dict[str, Callable] = {}
        self.message_handlers: List[Callable] = []
        self.callback_handlers: Dict[str, Callable] = {}
        self.running = False
        self.user: Optional[Dict] = None
        
    async def start(self):
        """Start the HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
            
        # Get bot info
        try:
            self.user = await self.get_me()
            logger.info(f"Bot started: {self.user.get('first_name', 'Unknown')}")
        except Exception as e:
            logger.warning(f"Could not get bot info: {e}")
            self.user = {"first_name": "BalletBot", "username": "balletbot"}
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the Bale API"""
        if not self.session:
            await self.start()
            
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data) as response:
                result = await response.json()
                
                if not response.ok:
                    logger.error(f"API request failed: {response.status} - {result}")
                    raise Exception(f"API request failed: {response.status}")
                
                return result
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    async def get_me(self) -> Dict[str, Any]:
        """Get bot information"""
        response = await self._make_request("GET", "getMe")
        return response["result"]
    
    async def get_updates(self, offset: int = 0, limit: int = 100, 
                         timeout: int = 0, allowed_updates: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get updates from Bale"""
        data = {
            "offset": offset,
            "limit": limit,
            "timeout": timeout
        }
        
        if allowed_updates:
            data["allowed_updates"] = allowed_updates
        
        response = await self._make_request("POST", "getUpdates", data)
        return response.get("result", [])
    
    async def send_message(self, chat_id: str, text: str, 
                          reply_markup: Optional[Any] = None,
                          parse_mode: str = "Markdown") -> bool:
        """Send a text message"""
        try:
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            if reply_markup:
                data["reply_markup"] = reply_markup if isinstance(reply_markup, dict) else reply_markup.to_dict()
            
            await self._make_request("POST", "sendMessage", data)
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False
    
    async def send_photo(self, chat_id: str, photo_path: str, 
                        caption: str = "", 
                        reply_markup: Optional[Any] = None) -> bool:
        """Send a photo"""
        try:
            data = aiohttp.FormData()
            data.add_field('chat_id', chat_id)
            data.add_field('photo', open(photo_path, 'rb'), filename=photo_path)
            
            if caption:
                data.add_field('caption', caption)
            
            if reply_markup:
                data.add_field('reply_markup', json.dumps(reply_markup if isinstance(reply_markup, dict) else reply_markup.to_dict()))
            
            if not self.session:
                await self.start()
                
            url = f"{self.base_url}/sendPhoto"
            async with self.session.post(url, data=data) as response:
                result = await response.json()
                return response.ok and result.get("ok", False)
                
        except Exception as e:
            logger.error(f"Failed to send photo to {chat_id}: {e}")
            return False
    
    async def send_document(self, chat_id: str, document_path: str, 
                           caption: str = "") -> bool:
        """Send a document"""
        try:
            data = aiohttp.FormData()
            data.add_field('chat_id', chat_id)
            data.add_field('document', open(document_path, 'rb'), filename=document_path)
            
            if caption:
                data.add_field('caption', caption)
            
            if not self.session:
                await self.start()
                
            url = f"{self.base_url}/sendDocument"
            async with self.session.post(url, data=data) as response:
                result = await response.json()
                return response.ok and result.get("ok", False)
                
        except Exception as e:
            logger.error(f"Failed to send document to {chat_id}: {e}")
            return False
    
    async def edit_message_text(self, chat_id: str, message_id: int, text: str,
                               reply_markup: Optional[Any] = None) -> bool:
        """Edit message text"""
        try:
            data = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text
            }
            
            if reply_markup:
                data["reply_markup"] = reply_markup if isinstance(reply_markup, dict) else reply_markup.to_dict()
            
            await self._make_request("POST", "editMessageText", data)
            return True
        except Exception as e:
            logger.error(f"Failed to edit message in {chat_id}: {e}")
            return False
    
    async def answer_callback_query(self, callback_query_id: str, text: str = "", 
                                   show_alert: bool = False) -> bool:
        """Answer a callback query"""
        try:
            data = {
                "callback_query_id": callback_query_id,
                "text": text,
                "show_alert": show_alert
            }
            
            await self._make_request("POST", "answerCallbackQuery", data)
            return True
        except Exception as e:
            logger.error(f"Failed to answer callback query: {e}")
            return False
    
    async def is_admin(self, chat_id: str, user_id: str) -> bool:
        """Check if user is admin in chat"""
        try:
            data = {"chat_id": chat_id, "user_id": user_id}
            response = await self._make_request("POST", "getChatMember", data)
            member = response["result"]
            return member.get("status") in ['creator', 'administrator']
        except Exception as e:
            logger.error(f"Failed to check admin status: {e}")
            return False
    
    async def get_chat_member(self, chat_id: str, user_id: str) -> Optional[Dict]:
        """Get chat member information"""
        try:
            data = {"chat_id": chat_id, "user_id": user_id}
            response = await self._make_request("POST", "getChatMember", data)
            return response["result"]
        except Exception as e:
            logger.error(f"Failed to get chat member: {e}")
            return None
    
    def create_inline_keyboard(self, buttons: List[List[Dict[str, str]]]) -> Dict:
        """Create inline keyboard markup"""
        return {
            "inline_keyboard": buttons
        }
    
    async def process_update(self, update: Dict[str, Any]):
        """Process incoming update"""
        try:
            if "message" in update:
                await self._process_message(update["message"])
            elif "callback_query" in update:
                await self._process_callback_query(update["callback_query"])
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    async def _process_message(self, message: Dict[str, Any]):
        """Process incoming message"""
        try:
            if not message.get("text"):
                return
            
            text = message["text"].strip()
            chat_id = str(message["chat"]["id"])
            user_id = str(message["from"]["id"])
            
            # Check for commands
            if text.startswith('/'):
                command_parts = text.split(' ', 1)
                command = command_parts[0]
                args = command_parts[1] if len(command_parts) > 1 else ""
                
                if command in self.command_handlers:
                    try:
                        # Create mock message object
                        mock_message = type('Message', (), {
                            'chat': type('Chat', (), {'id': message["chat"]["id"]})(),
                            'from_user': type('User', (), {'id': message["from"]["id"]})(),
                            'text': message["text"]
                        })()
                        
                        await self.command_handlers[command](mock_message, args)
                    except Exception as e:
                        logger.error(f"Error in command handler {command}: {e}")
                        await self.send_message(chat_id, "❌ An error occurred processing your command.")
                else:
                    # Try message handlers
                    for handler in self.message_handlers:
                        try:
                            mock_message = type('Message', (), {
                                'chat': type('Chat', (), {'id': message["chat"]["id"]})(),
                                'from_user': type('User', (), {'id': message["from"]["id"]})(),
                                'text': message["text"]
                            })()
                            await handler(mock_message)
                        except Exception as e:
                            logger.error(f"Error in message handler: {e}")
            else:
                # Process as regular message
                for handler in self.message_handlers:
                    try:
                        mock_message = type('Message', (), {
                            'chat': type('Chat', (), {'id': message["chat"]["id"]})(),
                            'from_user': type('User', (), {'id': message["from"]["id"]})(),
                            'text': message["text"]
                        })()
                        await handler(mock_message)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
                        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _process_callback_query(self, callback_query: Dict[str, Any]):
        """Process callback query"""
        try:
            data = callback_query.get("data")
            chat_id = str(callback_query["message"]["chat"]["id"])
            user_id = str(callback_query["from"]["id"])
            
            if data in self.callback_handlers:
                try:
                    mock_callback = type('CallbackQuery', (), {
                        'id': callback_query["id"],
                        'data': data,
                        'message': type('Message', (), {
                            'chat': type('Chat', (), {'id': callback_query["message"]["chat"]["id"]})(),
                            'from_user': type('User', (), {'id': callback_query["from"]["id"]})()
                        })()
                    })()
                    
                    await self.callback_handlers[data](mock_callback)
                except Exception as e:
                    logger.error(f"Error in callback handler {data}: {e}")
                    await self.answer_callback_query(callback_query["id"], "❌ An error occurred.")
                    
        except Exception as e:
            logger.error(f"Error processing callback query: {e}")
    
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
    
    async def start_polling(self, update_handler: Optional[Callable] = None,
                           allowed_updates: Optional[List[str]] = None):
        """Start polling for updates"""
        logger.info("Starting Bale bot polling...")
        self.running = True
        
        try:
            await self.start()
            
            offset = 0
            while self.running:
                try:
                    updates = await self.get_updates(
                        offset=offset, 
                        allowed_updates=allowed_updates or ['message', 'callback_query']
                    )
                    
                    for update in updates:
                        if update_handler:
                            await update_handler(update)
                        else:
                            await self.process_update(update)
                        
                        offset = update["update_id"] + 1
                    
                    await asyncio.sleep(1)  # Polling interval
                    
                except Exception as e:
                    logger.error(f"Error in polling loop: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Error in polling: {e}")
            raise
    
    async def stop_polling(self):
        """Stop polling"""
        logger.info("Stopping Bale bot polling...")
        self.running = False
        await self.close()
    
    def get_user_info(self, user) -> User:
        """Extract user information from Bale user object"""
        if hasattr(user, 'id'):
            return User(
                id=str(user.id),
                username=getattr(user, 'username', '') or "",
                first_name=getattr(user, 'first_name', '') or "",
                last_name=getattr(user, 'last_name', None),
                is_bot=getattr(user, 'is_bot', False)
            )
        else:
            # Mock user for testing
            return User(
                id="mock_user",
                username="mock_user",
                first_name="Mock",
                last_name="User",
                is_bot=False
            )