# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import List, Dict, Any
from .menukeyboardbutton import MenuKeyboardButton

class MenuKeyboardMarkup:
    """Menu keyboard markup"""
    
    def __init__(self, keyboard: List[List[MenuKeyboardButton]]):
        self.keyboard = keyboard
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "keyboard": [
                [button.to_dict() for button in row] 
                for row in self.keyboard
            ]
        }