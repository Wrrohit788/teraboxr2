from config import *
import telethon
from telethon import TelegramClient, events

bot = TelegramClient("tele", API_ID, API_HASH)

bot_un = None

async def get_un():
    global bot_un
    if bot_un:
        return bot_un
    else:
        bot_un = (await bot.get_me()).username
        return bot_un
