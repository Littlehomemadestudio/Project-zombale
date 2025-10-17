# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import Any, Dict, Optional

class User:
    """User object"""
    
    def __init__(self, id: int, first_name: str, last_name: Optional[str] = None,
                 username: Optional[str] = None, is_bot: bool = False):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.is_bot = is_bot
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User from dictionary"""
        return cls(
            id=data["id"],
            first_name=data["first_name"],
            last_name=data.get("last_name"),
            username=data.get("username"),
            is_bot=data.get("is_bot", False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "id": self.id,
            "first_name": self.first_name,
            "is_bot": self.is_bot
        }
        
        if self.last_name:
            result["last_name"] = self.last_name
        
        if self.username:
            result["username"] = self.username
        
        return result
    
    @property
    def mention(self) -> str:
        """Get user mention"""
        if self.username:
            return f"@{self.username}"
        return self.first_name