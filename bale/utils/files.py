# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import Union, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .types import FileInput, InputFile

def parse_file_input(file_input: 'FileInput') -> Any:
    """Parse file input for API requests"""
    if isinstance(file_input, str):
        # File path
        return open(file_input, 'rb')
    elif isinstance(file_input, bytes):
        # Raw bytes
        return file_input
    elif hasattr(file_input, 'read'):
        # File-like object
        return file_input
    else:
        raise ValueError("Invalid file input type")