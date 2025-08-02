import dotenv
import asyncio
import os
from configs import phrases
from configs import config
from aiogram import Bot, Dispatcher, filters, types
from aiogram.enums import ParseMode
from loguru import logger
from catgirl import CatgirlDownloaderAPI
from middlewares import AntiFlood, RateLimit
from colorama import Fore

dotenv.load_dotenv() # import .env

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
ct = CatgirlDownloaderAPI()
queue = []

@dp.startup()
async def on_startup():
    me = await bot.get_me()
    logger.info(f"Bot started as {Fore.BLUE}@{me.username} {Fore.LIGHTMAGENTA_EX}:3")

@dp.message(filters.CommandStart())
async def start(message: types.Message):
    try:
        await message.reply(phrases.WELCOME, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(e)

@dp.message(filters.Command(commands=["meow", "nsfw"]))
async def meow(message: types.Message):
    try:
        user_id  = message.from_user.id
        if user_id in queue:
            await message.reply(phrases.QUEUE_DENY, parse_mode=ParseMode.HTML)
            return
        is_nsfw= True if "nsfw" in message.text else False
        caption = phrases.NSFW_CAPTION if "nsfw" in message.text else phrases.SFW_CAPTION
        queue.append(user_id)
        url = ct.get_neko(nsfw=is_nsfw)
        if url:
            logger.debug(f"Image URL: {Fore.WHITE}{url} ({caption})")
            await message.reply_photo(url, caption=caption, has_spoiler=is_nsfw, parse_mode=ParseMode.HTML)
            queue.remove(user_id)
    except Exception as e:
        if user_id in queue:
            queue.remove(user_id) # remove from queue if error
        logger.error(e)
        await message.reply(phrases.ERROR_MESSAGE, parse_mode=ParseMode.HTML)

async def main():
    # middlewares:
    dp.message.middleware(AntiFlood(limit=config.ANTIFLOOD_INTERVAL))
    dp.message.middleware(RateLimit(
        max_requests=config.RATELIMIT["max_requests"], 
        per_seconds=config.RATELIMIT["per_seconds"], 
        ban_time=config.RATELIMIT["ban_time"]
    ))
    # run:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())