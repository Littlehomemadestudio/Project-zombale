# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import Any, Dict, Optional

class Chat:
    """Chat object"""
    
    def __init__(self, id: int, type: str, title: Optional[str] = None,
                 username: Optional[str] = None, first_name: Optional[str] = None,
                 last_name: Optional[str] = None):
        self.id = id
        self.type = type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chat':
        """Create Chat from dictionary"""
        return cls(
            id=data["id"],
            type=data["type"],
            title=data.get("title"),
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "id": self.id,
            "type": self.type
        }
        
        if self.title:
            result["title"] = self.title
        
        if self.username:
            result["username"] = self.username
        
        if self.first_name:
            result["first_name"] = self.first_name
        
        if self.last_name:
            result["last_name"] = self.last_name
        
        return result