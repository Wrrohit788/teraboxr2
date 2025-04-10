from config import *
import telethon
import redis
from telethon import TelegramClient, events

db = redis.Redis(
    host=HOST,
    port=PORT,
    password=PASSWORD,
    decode_responses=True,
)

bot = TelegramClient("tele", API_ID, API_HASH)

bot_un = None

async def get_un():
    global bot_un
    if bot_un:
        return bot_un
    else:
        bot_un = (await bot.get_me()).username
        return bot_un
