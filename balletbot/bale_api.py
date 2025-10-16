"""
Bale API wrapper with mock implementation for development
Replace this with actual bale.Bot integration in production
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class User:
    """Mock user object"""
    id: str
    username: str
    first_name: str
    last_name: Optional[str] = None

@dataclass
class Message:
    """Mock message object"""
    id: str
    text: str
    user: User
    chat_id: str
    is_private: bool = False

class BaleAPI:
    """Bale API wrapper with mock implementation for development"""
    
    def __init__(self, token: str = "mock_token"):
        self.token = token
        self.command_handlers: Dict[str, Callable] = {}
        self.message_handlers: List[Callable] = []
        self.running = False
        
        # Mock data for testing
        self.mock_users = {
            "user1": User("user1", "testuser1", "Test", "User1"),
            "user2": User("user2", "testuser2", "Test", "User2"),
            "admin1": User("admin1", "admin", "Admin", "User"),
        }
        
        self.mock_messages = []
        
    def command(self, command: str):
        """Decorator to register command handlers"""
        def decorator(func):
            self.command_handlers[command] = func
            return func
        return decorator
    
    def message_handler(self, func):
        """Decorator to register message handlers"""
        self.message_handlers.append(func)
        return func
    
    async def send_message(self, chat_id: str, text: str, reply_to: Optional[str] = None, 
                          parse_mode: str = "HTML", **kwargs) -> bool:
        """Send a message to a chat"""
        logger.info(f"Sending message to {chat_id}: {text[:100]}...")
        
        # In mock mode, just log the message
        if chat_id.startswith("group_"):
            logger.info(f"[GROUP {chat_id}] {text}")
        else:
            logger.info(f"[PV {chat_id}] {text}")
            
        return True
    
    async def send_photo(self, chat_id: str, photo_path: str, caption: str = "", 
                        reply_to: Optional[str] = None, **kwargs) -> bool:
        """Send a photo to a chat"""
        logger.info(f"Sending photo to {chat_id}: {photo_path} (caption: {caption})")
        return True
    
    async def send_document(self, chat_id: str, document_path: str, caption: str = "", 
                           reply_to: Optional[str] = None, **kwargs) -> bool:
        """Send a document to a chat"""
        logger.info(f"Sending document to {chat_id}: {document_path} (caption: {caption})")
        return True
    
    async def get_chat_administrators(self, chat_id: str) -> List[User]:
        """Get chat administrators"""
        # Mock: return admin users
        return [self.mock_users["admin1"]]
    
    async def get_chat_member(self, chat_id: str, user_id: str) -> Optional[User]:
        """Get chat member info"""
        return self.mock_users.get(user_id)
    
    async def is_admin(self, chat_id: str, user_id: str) -> bool:
        """Check if user is admin in chat"""
        admins = await self.get_chat_administrators(chat_id)
        return any(admin.id == user_id for admin in admins)
    
    def create_message(self, text: str, user_id: str, chat_id: str, is_private: bool = False) -> Message:
        """Create a mock message for testing"""
        user = self.mock_users.get(user_id, User(user_id, f"user{user_id}", "Unknown"))
        return Message(
            id=f"msg_{len(self.mock_messages)}",
            text=text,
            user=user,
            chat_id=chat_id,
            is_private=is_private
        )
    
    async def process_message(self, message: Message):
        """Process an incoming message"""
        if not message.text:
            return
            
        # Check for commands
        if message.text.startswith('/'):
            parts = message.text.split()
            command = parts[0][1:]  # Remove leading slash
            
            if command in self.command_handlers:
                try:
                    await self.command_handlers[command](message)
                except Exception as e:
                    logger.error(f"Error handling command {command}: {e}")
                    await self.send_message(
                        message.chat_id,
                        f"❌ Error processing command: {str(e)}",
                        reply_to=message.id
                    )
            else:
                await self.send_message(
                    message.chat_id,
                    f"❓ Unknown command: /{command}",
                    reply_to=message.id
                )
        else:
            # Process as regular message
            for handler in self.message_handlers:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")
    
    async def start_polling(self):
        """Start polling for messages (mock implementation)"""
        logger.info("Starting Bale API polling (mock mode)")
        self.running = True
        
        # In mock mode, we'll simulate some test messages
        await self._simulate_test_messages()
    
    async def stop_polling(self):
        """Stop polling for messages"""
        logger.info("Stopping Bale API polling")
        self.running = False
    
    async def _simulate_test_messages(self):
        """Simulate test messages for development"""
        test_messages = [
            ("/start", "user1", "group_test", False),
            ("/join ABC123", "user1", "user1", True),
            ("/create_character Ash Scavenger", "user1", "user1", True),
            ("/status", "user1", "user1", True),
            ("/map", "user1", "user1", True),
        ]
        
        for text, user_id, chat_id, is_private in test_messages:
            if not self.running:
                break
                
            message = self.create_message(text, user_id, chat_id, is_private)
            await self.process_message(message)
            await asyncio.sleep(1)  # Simulate delay between messages

# Global instance for easy access
bale_api = BaleAPI()