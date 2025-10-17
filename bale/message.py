# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import Any, Dict, Optional
from .user import User
from .chat import Chat

class Message:
    """Message object"""
    
    def __init__(self, message_id: int, from_user: Optional[User] = None, 
                 chat: Optional[Chat] = None, text: Optional[str] = None,
                 date: Optional[int] = None):
        self.message_id = message_id
        self.from_user = from_user
        self.chat = chat
        self.text = text
        self.date = date
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create Message from dictionary"""
        from_user = None
        chat = None
        
        if "from" in data:
            from_user = User.from_dict(data["from"])
        
        if "chat" in data:
            chat = Chat.from_dict(data["chat"])
        
        return cls(
            message_id=data["message_id"],
            from_user=from_user,
            chat=chat,
            text=data.get("text"),
            date=data.get("date")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {"message_id": self.message_id}
        
        if self.from_user:
            result["from"] = self.from_user.to_dict()
        
        if self.chat:
            result["chat"] = self.chat.to_dict()
        
        if self.text:
            result["text"] = self.text
        
        if self.date:
            result["date"] = self.date
        
        return result
    
    async def reply(self, text: str, **kwargs) -> 'Message':
        """Reply to this message"""
        # This would need the bot instance to work properly
        # For now, return a mock message
        return Message(message_id=self.message_id + 1, text=text)