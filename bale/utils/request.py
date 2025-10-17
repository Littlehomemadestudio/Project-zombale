# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import Any, Dict, Optional
from enum import Enum

class ResponseStatusCode(Enum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

def to_json(data: Any) -> str:
    """Convert data to JSON string"""
    import json
    return json.dumps(data)

def find_error_class(status_code: int) -> str:
    """Find error class based on status code"""
    if status_code == 400:
        return "BadRequest"
    elif status_code == 401:
        return "Unauthorized"
    elif status_code == 403:
        return "Forbidden"
    elif status_code == 404:
        return "NotFound"
    elif status_code >= 500:
        return "InternalServerError"
    else:
        return "APIError"

class RequestParams:
    """Request parameters container"""
    def __init__(self, **kwargs):
        self.params = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        return self.params