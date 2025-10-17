# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import List, Dict, Any
from .inlinekeyboardbutton import InlineKeyboardButton

class InlineKeyboardMarkup:
    """Inline keyboard markup"""
    
    def __init__(self, inline_keyboard: List[List[InlineKeyboardButton]]):
        self.inline_keyboard = inline_keyboard
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "inline_keyboard": [
                [button.to_dict() for button in row] 
                for row in self.inline_keyboard
            ]
        }