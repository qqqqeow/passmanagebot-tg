from typing import Any, Dict, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from config import ADMINS_ID


class AdminMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.from_user.id in ADMINS_ID:
            return await handler(event, data)

class AdminCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        if event.from_user.id in ADMINS_ID:
            return await handler(event, data)
        return