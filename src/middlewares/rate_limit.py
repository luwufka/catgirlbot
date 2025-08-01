import time
from configs import phrases
from aiogram import BaseMiddleware, types, enums, exceptions
from collections import defaultdict

class RateLimit(BaseMiddleware):
    def __init__(self, max_requests: int = 5, per_seconds: int = 10, ban_time: int = 30):
        """
        :param max_requests: сколько сообщений можно отправить
        :param per_seconds: за сколько секунд (окно)
        :param ban_time: на сколько секунд забанить
        """
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self.ban_time = ban_time
        self.user_requests = defaultdict(list)  # user_id -> [timestamps]
        self.banned_until = {}  # user_id -> timestamp

    async def __call__(self, handler, event: types.Message, data):
        user_id = event.from_user.id
        now = time.time()

        ban_expire = self.banned_until.get(user_id)
        if ban_expire and now < ban_expire:
            return

        timestamps = self.user_requests[user_id]
        timestamps = [ts for ts in timestamps if now - ts <= self.per_seconds]
        timestamps.append(now)
        self.user_requests[user_id] = timestamps

        if len(timestamps) > self.max_requests:
            self.banned_until[user_id] = now + self.ban_time
            self.user_requests[user_id] = []
            try:
                await event.answer(phrases.RATELIMIT_MESSAGE, parse_mode=enums.ParseMode.HTML)
            except exceptions.TelegramBadRequest:
                pass
            return

        return await handler(event, data)