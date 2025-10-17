# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

class BaleError(Exception):
    """Base exception for Bale API errors"""
    pass

class HTTPClientError(BaleError):
    """HTTP client error"""
    pass

class APIError(BaleError):
    """Bale API error"""
    pass

class NetworkError(BaleError):
    """Network error"""
    pass

class TimeOut(BaleError):
    """Request timeout error"""
    pass

class HTTPException(BaleError):
    """HTTP exception"""
    pass

__ERROR_CLASSES__ = {
    "HTTPClientError": HTTPClientError,
    "APIError": APIError,
    "NetworkError": NetworkError,
    "TimeOut": TimeOut,
    "HTTPException": HTTPException
}