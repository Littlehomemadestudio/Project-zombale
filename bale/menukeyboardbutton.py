# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import Any, Dict, Optional

class MenuKeyboardButton:
    """Menu keyboard button"""
    
    def __init__(self, text: str, **kwargs):
        self.text = text
        self.other_data = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {"text": self.text}
        result.update(self.other_data)
        return result