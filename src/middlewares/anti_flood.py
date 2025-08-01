from aiogram import BaseMiddleware, types
from loguru import logger
import time

class AntiFlood(BaseMiddleware):
    def __init__(self, limit=1.4):
        self.limit = limit
        self.last_time = {}

    async def __call__(self, handler, event: types.Message, data):
        user_id = event.from_user.id
        now = time.time()
        last = self.last_time.get(user_id, 0)

        if now - last < self.limit:
            return

        self.last_time[user_id] = now
        return await handler(event, data)