# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

import json
from typing import Any, Dict
from aiohttp import ClientResponse
from bale.utils.request import ResponseStatusCode

class ResponseParser:
    """Response parser for Bale API"""
    
    @staticmethod
    async def parse_response(response: ClientResponse) -> 'ResponseParser':
        """Parse HTTP response"""
        data = await response.json()
        return ResponseParser(
            ok=data.get("ok", False),
            result=data.get("result"),
            error_code=data.get("error_code"),
            description=data.get("description"),
            status_code=response.status
        )
    
    def __init__(self, ok: bool = False, result: Any = None, 
                 error_code: int = None, description: str = None, 
                 status_code: int = 200):
        self.ok = ok
        self.result = result
        self.error_code = error_code
        self.description = description
        self.status_code = status_code