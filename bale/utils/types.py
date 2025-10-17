# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.

from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from bale import Update, Message, CallbackQuery
    from bale.attachments import InputFile

UT = TypeVar('UT', bound='Update')
AttachmentType = str
FileInput = Union[str, bytes, 'InputFile']