# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import Any, Dict, Optional

class InlineKeyboardButton:
    """Inline keyboard button"""
    
    def __init__(self, text: str, callback_data: Optional[str] = None,
                 url: Optional[str] = None, **kwargs):
        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.other_data = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {"text": self.text}
        
        if self.callback_data:
            result["callback_data"] = self.callback_data
        
        if self.url:
            result["url"] = self.url
        
        result.update(self.other_data)
        return result