"""
Simplified Bale API wrapper for BalletBot: Outbreak Dominion
Handles Bale messenger integration using a simplified approach
"""

import asyncio
import logging
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
    """Simplified Bale API wrapper for the bot"""
    
    def __init__(self, token: str):
        self.token = token
        self.command_handlers: Dict[str, Callable] = {}
        self.message_handlers: List[Callable] = []
        self.callback_handlers: Dict[str, Callable] = {}
        self.running = False
        
        # Mock bot info for testing
        self.user = {
            "id": 123456789,
            "first_name": "BalletBot",
            "username": "balletbot",
            "is_bot": True
        }
        
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
                          reply_markup: Optional[Any] = None,
                          parse_mode: str = "Markdown") -> bool:
        """Send a text message"""
        try:
            logger.info(f"[BALE API] Sending message to {chat_id}: {text[:100]}...")
            if reply_markup:
                logger.info(f"[BALE API] With reply markup: {reply_markup}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False
    
    async def send_photo(self, chat_id: str, photo_path: str, 
                        caption: str = "", 
                        reply_markup: Optional[Any] = None) -> bool:
        """Send a photo"""
        try:
            logger.info(f"[BALE API] Sending photo to {chat_id}: {photo_path}")
            if caption:
                logger.info(f"[BALE API] Caption: {caption}")
            if reply_markup:
                logger.info(f"[BALE API] With reply markup: {reply_markup}")
            return True
        except Exception as e:
            logger.error(f"Failed to send photo to {chat_id}: {e}")
            return False
    
    async def send_document(self, chat_id: str, document_path: str, 
                           caption: str = "") -> bool:
        """Send a document"""
        try:
            logger.info(f"[BALE API] Sending document to {chat_id}: {document_path}")
            if caption:
                logger.info(f"[BALE API] Caption: {caption}")
            return True
        except Exception as e:
            logger.error(f"Failed to send document to {chat_id}: {e}")
            return False
    
    async def edit_message_text(self, chat_id: str, message_id: int, text: str,
                               reply_markup: Optional[Any] = None) -> bool:
        """Edit message text"""
        try:
            logger.info(f"[BALE API] Editing message {message_id} in {chat_id}: {text[:100]}...")
            if reply_markup:
                logger.info(f"[BALE API] With reply markup: {reply_markup}")
            return True
        except Exception as e:
            logger.error(f"Failed to edit message in {chat_id}: {e}")
            return False
    
    async def answer_callback_query(self, callback_query_id: str, text: str = "", 
                                   show_alert: bool = False) -> bool:
        """Answer a callback query"""
        try:
            logger.info(f"[BALE API] Answering callback query {callback_query_id}: {text}")
            return True
        except Exception as e:
            logger.error(f"Failed to answer callback query: {e}")
            return False
    
    async def is_admin(self, chat_id: str, user_id: str) -> bool:
        """Check if user is admin in chat"""
        try:
            logger.info(f"[BALE API] Checking admin status for {user_id} in {chat_id}")
            # Mock admin check - return True for testing
            return True
        except Exception as e:
            logger.error(f"Failed to check admin status: {e}")
            return False
    
    async def get_chat_member(self, chat_id: str, user_id: str) -> Optional[Dict]:
        """Get chat member information"""
        try:
            logger.info(f"[BALE API] Getting chat member {user_id} from {chat_id}")
            return {"id": user_id, "status": "member"}
        except Exception as e:
            logger.error(f"Failed to get chat member: {e}")
            return None
    
    def create_inline_keyboard(self, buttons: List[List[Dict[str, str]]]) -> Dict:
        """Create inline keyboard markup"""
        logger.info(f"[BALE API] Creating inline keyboard with {len(buttons)} rows")
        return {"keyboard": buttons}
    
    async def process_update(self, update: Dict[str, Any]):
        """Process incoming update"""
        try:
            logger.info(f"[BALE API] Processing update: {update}")
            
            # Mock update processing
            if "message" in update:
                message = update["message"]
                if message.get("text", "").startswith("/"):
                    # Handle command
                    command = message["text"].split()[0]
                    args = " ".join(message["text"].split()[1:]) if len(message["text"].split()) > 1 else ""
                    
                    if command in self.command_handlers:
                        # Create mock message object
                        mock_message = type('Message', (), {
                            'chat': type('Chat', (), {'id': message.get("chat", {}).get("id", "123456789")})(),
                            'from_user': type('User', (), {'id': message.get("from", {}).get("id", "987654321")})(),
                            'text': message.get("text", "")
                        })()
                        
                        await self.command_handlers[command](mock_message, args)
            
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    async def start_polling(self, update_handler: Optional[Callable] = None,
                           allowed_updates: Optional[List[str]] = None):
        """Start polling for updates"""
        logger.info("Starting Bale bot polling...")
        self.running = True
        
        try:
            # Mock polling - just log that it started
            logger.info("Bale bot polling started (mock mode)")
            
            # In a real implementation, this would start the actual polling loop
            # For now, we'll just simulate it
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in polling: {e}")
            raise
    
    async def stop_polling(self):
        """Stop polling"""
        logger.info("Stopping Bale bot polling...")
        self.running = False
    
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