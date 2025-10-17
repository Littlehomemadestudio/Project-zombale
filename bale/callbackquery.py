# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import Any, Dict, Optional
from .user import User
from .message import Message

class CallbackQuery:
    """Callback query object"""
    
    def __init__(self, id: str, from_user: Optional[User] = None, 
                 message: Optional[Message] = None, data: Optional[str] = None):
        self.id = id
        self.from_user = from_user
        self.message = message
        self.data = data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CallbackQuery':
        """Create CallbackQuery from dictionary"""
        from_user = None
        message = None
        
        if "from" in data:
            from_user = User.from_dict(data["from"])
        
        if "message" in data:
            message = Message.from_dict(data["message"])
        
        return cls(
            id=data["id"],
            from_user=from_user,
            message=message,
            data=data.get("data")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {"id": self.id}
        
        if self.from_user:
            result["from"] = self.from_user.to_dict()
        
        if self.message:
            result["message"] = self.message.to_dict()
        
        if self.data:
            result["data"] = self.data
        
        return result