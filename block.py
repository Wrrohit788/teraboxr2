import time
from telethon import events, TelegramClient
from func import bot 

block_watcher = 69

dic1 = {}
dic2 = {}
block = {}

def is_blocked(user_id):
    if user_id in block:
        if int(time.time() - block[user_id]) > 600:
            block.pop(user_id)
    return user_id in block

@bot.on(events.NewMessage(incoming=True))
async def block_cwf(event):
    if event.chat_id != event.sender_id: 
        return

    user_id = event.sender_id
    if user_id in block:
        return

    if user_id in dic1:
        if int(time.time() - dic1[user_id]) <= 1:
            if user_id in dic2:
                dic2[user_id] += 1
            else:
                dic2[user_id] = 1
            if dic2[user_id] >= 4:
                dic2[user_id] = 0
                block[user_id] = time.time()
                txt = "You have been blocked for 10 minutes due to flooding ⚠️"
                await event.respond(txt)
        else:
            dic2[user_id] = 0
        dic1[user_id] = time.time()
    else:
        dic1[user_id] = time.time()
