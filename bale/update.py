# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import Any, Dict, Optional
from .message import Message
from .callbackquery import CallbackQuery

class Update:
    """Update object representing an incoming update"""
    
    def __init__(self, update_id: int, message: Optional[Message] = None, 
                 callback_query: Optional[CallbackQuery] = None):
        self.update_id = update_id
        self.message = message
        self.callback_query = callback_query
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Update':
        """Create Update from dictionary"""
        message = None
        callback_query = None
        
        if "message" in data:
            message = Message.from_dict(data["message"])
        
        if "callback_query" in data:
            callback_query = CallbackQuery.from_dict(data["callback_query"])
        
        return cls(
            update_id=data["update_id"],
            message=message,
            callback_query=callback_query
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {"update_id": self.update_id}
        
        if self.message:
            result["message"] = self.message.to_dict()
        
        if self.callback_query:
            result["callback_query"] = self.callback_query.to_dict()
        
        return result