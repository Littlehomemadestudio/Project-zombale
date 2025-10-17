# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import Union, BinaryIO
from ._basefile import BaseFile

class InputFile(BaseFile):
    """Input file for uploads"""
    
    def __init__(self, file: Union[str, BinaryIO], filename: str = None):
        self.file = file
        self.filename = filename or getattr(file, 'name', 'file')
    
    def to_multipart_payload(self) -> dict:
        """Convert to multipart payload"""
        return {
            'value': self.file,
            'filename': self.filename
        }