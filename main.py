import asyncio
import os
import time
from datetime import timedelta
import random
from uuid import uuid4
from telethon import Button
import telethon
from telethon import TelegramClient, events
from telethon.tl import functions
from telethon.types import Message, UpdateNewMessage
from telethon.tl.functions.messages import ForwardMessagesRequest
from cansend import CanSend
from config import *
from terabox import get_data
from get_link import post
from db import *
import string
from tools import *
from config import BOT_TOKEN
import os
import time
import subprocess
from uuid import uuid4
from telethon.tl.functions.messages import ForwardMessagesRequest
from download import download_file
import aiohttp
import io
from string import ascii_uppercase, digits
from motor.motor_asyncio import AsyncIOMotorClient
from telethon.errors import UserBlockedError, UserDeactivatedError
from block import is_blocked
from func import *

MAX_RETRIES = 3

dev_users = [5960968099, 7758708579]

start_time = time.time()

CHANNEL_SUPPORT = "AlphaBotzchat"
CHANNEL_UPDATE = "AlphaBotz"
CHANNEL_SUPPORT_ID = -1002198026757
CHANNEL_UPDATE_ID = -1002121014023

mongo_client = AsyncIOMotorClient(MONGO_DB_URL)
bc = mongo_client[DB_NAME]

user_tokens_collection = bc["user_tokens"]
settings_collection = bc["settings"]
premium_users_collection = bc["premium_users"]
file_cache_collection = bc["file_cache"]
gift_codes_collection = bc["gift_codes"]
counters_collection = bc["counters"]

@bot.on(events.NewMessage(pattern="/ads (on|off)", incoming=True))
async def toggle_ads_verification(event):
    if event.sender_id not in dev_users:
        return await event.reply("You are not authorized to use this command.")

    action = event.pattern_match.group(1)

    if action == "on":
        await settings_collection.update_one(
            {"_id": "ads_verification"},
            {"$set": {"state": "on"}},
            upsert=True
        )
        await event.reply("Ads verification enabled.")
    elif action == "off":
        await settings_collection.update_one(
            {"_id": "ads_verification"},
            {"$set": {"state": "off"}},
            upsert=True
        )
        await event.reply("Ads verification disabled.")
    else:
        await event.reply("Invalid command usage. Please use `/ads on` or `/ads off`.")

async def ads_verification_required(user_id):
    ads_doc = await settings_collection.find_one({"_id": "ads_verification"})
    ads_state = ads_doc["state"] if ads_doc else "off"
    if ads_state == "off":
        return False
    else:
        pr_user = await premium_users_collection.find_one({"user_id": str(user_id)})
        if pr_user:
            return False
        else:
            token = await get_token(user_id)
            if not token[0] or int(time.time() - token[1]) > 86400:
                return True
            else:
                return False

@bot.on(events.NewMessage(pattern="/start", incoming=True))
async def start_command(event):
    if event.is_group:
        return

    user_id = event.sender_id
    if is_blocked(user_id):
        return

    user = await user_tokens_collection.find_one({"user_id": user_id})

    if not user:
        token = ''.join(random.choices(ascii_uppercase + digits, k=15))
        await user_tokens_collection.insert_one({
            "user_id": user_id,
            "token": token,
            "verified": False,
            "is_premium": False
        })

    if await ads_verification_required(user_id):
        await event.respond(
            "Please join both support and update channels before using the bot.",
            buttons=[
                [Button.url("Join Support", f"https://t.me/{CHANNEL_SUPPORT}")],
                [Button.url("Join Update", f"https://t.me/{CHANNEL_UPDATE}")],
            ]
        )
        return

    join_support = not await is_user_on_chat(bot, CHANNEL_SUPPORT_ID, user_id)
    join_update = not await is_user_on_chat(bot, CHANNEL_UPDATE_ID, user_id)

    if join_support and join_update:
        await event.respond(
            "Please join both support and update channels before using the bot.",
            buttons=[
                [Button.url("Join Support", f"https://t.me/{CHANNEL_SUPPORT}")],
                [Button.url("Join Update", f"https://t.me/{CHANNEL_UPDATE}")],
            ]
        )
    elif join_support:
        await event.respond(
            "Please join support then send me the link again.",
            buttons=[Button.url("Join Support", f"https://t.me/{CHANNEL_SUPPORT}")]
        )
    elif join_update:
        await event.respond(
            "Please join update then send me the link again.",
            buttons=[Button.url("Join Update", f"https://t.me/{CHANNEL_UPDATE}")]
        )
    else:
        reply_markup = [
            [Button.url("Support 💌", f"https://t.me/{CHANNEL_SUPPORT}"),
             Button.url("Updates 📜", f"https://t.me/{CHANNEL_UPDATE}")]
        ]
        img_url = "https://graph.org/file/41421ca12a57a331f1756.jpg"
        caption = (
            "𝐇𝐞𝐥𝐥𝐨! 𝐈 𝐚𝐦 𝐓𝐞𝐫𝐚𝐛𝐨𝐱 𝐕𝐢𝐝𝐞𝐨 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐫 𝐁𝐨𝐭.\n\n"
            "𝐒𝐞𝐧𝐝 𝐦𝐞 𝐭𝐞𝐫𝐚𝐛𝐨𝐱 𝐯𝐢𝐤 𝐥𝐢𝐧𝐤 & 𝐈 𝐰𝐢𝐥𝐥 𝐬𝐞𝐧𝐝 𝐕𝐢𝐝𝐞𝐨.\n\n"
        )
        await bot.send_file(event.chat_id, file=img_url, caption=caption, buttons=reply_markup)

@bot.on(events.NewMessage(pattern="/start (.*)", incoming=True, outgoing=False))
async def start(m: UpdateNewMessage):
    text = m.pattern_match.group(1)

    if text.startswith('verify'):
        spl = text[7:]
        x = await get_verification_token(m.sender_id)
        if x != spl:
            return await m.reply('Invalid.')
        else:
            await update_token(m.sender_id, spl, time.time())
            await set_verification_token(m.sender_id, '')
            await m.reply('Success.')

    file_doc = await file_cache_collection.find_one({"_id": str(text)})
    fileid = file_doc["file_id"] if file_doc else None

    if fileid:
        await bot(
            ForwardMessagesRequest(
                from_peer=PRIVATE_CHAT_ID,
                id=[int(fileid)],
                to_peer=m.chat.id,
                drop_author=True,
                noforwards=False,
                background=True,
                drop_media_captions=False,
                with_my_score=True,
            )
        )

all = string.ascii_letters + string.digits + '_'
def generate_token(length: int) -> str:
    token = ''
    for i in range(length):
        token += random.choice(all)
    return token

@bot.on(events.NewMessage(pattern='/gen', incoming=True))
async def gen(e):
    if e.is_group:
        return
    user_id = e.sender_id
    if is_blocked(user_id):
        return

    pr_user = await premium_users_collection.find_one({"user_id": str(user_id)})
    if pr_user:
        return await e.reply("You are a premium user. No need to generate a token.")

    prev = await get_token(user_id)
    if prev[1]:
        if int(time.time() - prev[1]) < 86400:
            return await e.reply('You already have a valid token, no need to generate.')

    token = generate_token(30)
    await set_verification_token(user_id, token)
    un = await get_un()
    boo, x = post(f'https://t.me/{un}?start=verify_{token}')
    if not boo:
        return await e.reply(x)

    GEEK = Button.url("Link Here", url=x)
    INFO = Button.url("Tutorial ❓", url="https://t.me/Bypass_Shortlink/2")
    txt = f'Hey!\n\nYour Ads token is expired, refresh your token and try again.\n\nToken Timeout: 24 hours\n\nWhat is token?\n\nThis is an ads token.\n\nIf you pass 1 ad, you can use the bot for 24 hours after passing the ad.'
    await e.reply(txt, buttons=[[GEEK, INFO]])

@bot.on(
    events.NewMessage(
        incoming=True,
        outgoing=False,
        func=lambda message: message.text
        and get_urls_from_string(message.text)
        and message.is_private,
    )
)
async def handle_message(event, channel1=CHANNEL_UPDATE, channel2=CHANNEL_SUPPORT, channel1_id=CHANNEL_UPDATE_ID, channel2_id=CHANNEL_SUPPORT_ID):
    m = event.message
    sender_id = m.sender_id
    if is_blocked(sender_id):
        return

    if await ads_verification_required(sender_id):
        pr_user = await premium_users_collection.find_one({"user_id": str(sender_id)})
        if not pr_user:
            token = await get_token(sender_id)
            if not token[0]:
                return await m.reply('You do not have a token. Generate it by using /gen.')
            if int(time.time() - token[1]) > 86400:
                return await m.reply('You do not have a valid token. Generate it by using /gen.')

    url = get_urls_from_string(m.text)
    if not url:
        return await m.reply("Please enter a valid URL.")

    check_if_channel1 = await is_user_on_chat(bot, channel1_id, m.peer_id)
    if not check_if_channel1:
        return await m.reply(f"Please join https://t.me/{channel1} then send me the link again.")

    check_if_channel2 = await is_user_on_chat(bot, channel2_id, m.peer_id)
    if not check_if_channel2:
        return await m.reply(f"Please join https://t.me/{channel2} then send me the link again.")

    hm = await m.reply("Sending you the media, please wait...")

    shorturl = extract_code_from_url(url)
    if not shorturl:
        return await hm.edit("Seems like your link is invalid.")

    file_doc = await file_cache_collection.find_one({"_id": shorturl})
    fileid = file_doc["file_id"] if file_doc else None

    if fileid:
        try:
            await hm.delete()
        except:
            pass

        await bot(
            ForwardMessagesRequest(
                from_peer=PRIVATE_CHAT_ID,
                id=[int(fileid)],
                to_peer=m.chat.id,
                drop_author=True,
                noforwards=False,
                background=True,
                drop_media_captions=False,
                with_my_score=True,
            )
        )
        return

    await counters_collection.update_one(
        {"_id": f"check_{sender_id}"},
        {"$inc": {"count": 1}},
        upsert=True
    )

    data = await get_data(url)
    if not data:
        return await hm.edit("Sorry! your link is broken.")

    start_download_time = time.time()
    cansend = CanSend()
    download_path = None
    download_speed = 0

    async def progress_bar(current_downloaded, total_downloaded, state="Sending"):
        nonlocal start_download_time, download_speed
        if not cansend.can_send():
            return
        bar_length = 20
        percent = current_downloaded / total_downloaded
        arrow = "◉" * int(percent * bar_length)
        spaces = "◯" * (bar_length - len(arrow))

        elapsed_time = time.time() - start_download_time

        head_text = f"{state} `{data['file_name']}`"
        progress_bar = f"[{arrow + spaces}] {percent:.2%}"
        upload_speed = current_downloaded / elapsed_time if elapsed_time > 0 else 0
        speed_line = f"Speed: **{get_formatted_size(upload_speed)}/s**"

        time_remaining = (
            (total_downloaded - current_downloaded) / upload_speed
            if upload_speed > 0
            else 0
        )
        time_line = f"Time Remaining: `{convert_seconds(time_remaining)}`"

        size_line = f"Size: **{get_formatted_size(current_downloaded)}** / **{get_formatted_size(total_downloaded)}**"

        await hm.edit(
            f"{head_text}\n{progress_bar}\n{speed_line}\n{time_line}\n{size_line}",
            parse_mode="markdown",
        )

    uuid = str(uuid4())
    thumbnail = download_image_to_bytesio(data["thumb"], "thumbnail.png")

    async def aria2_download(url, output):
        cmd = [
            'aria2c',
            '--dir=/tmp',
            '--out=' + output,
            '--max-connection-per-server=16',
            '--split=16',
            '--min-split-size=1M',
            url
        ]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        return process.returncode, stdout, stderr

    async def handle_download(url, file_name, retry_message):
        nonlocal download_speed
        for attempt in range(MAX_RETRIES):
            start_download_time = time.time()
            returncode, stdout, stderr = await aria2_download(url, file_name + ".mp4")
            download_time = time.time() - start_download_time
            if returncode == 0:
                download_size = os.path.getsize(os.path.join("/tmp", file_name + ".mp4"))
                download_speed = download_size / download_time if download_time > 0 else 0
                return os.path.join("/tmp", file_name + ".mp4"), download_time
            else:
                if attempt < MAX_RETRIES - 1:
                    await hm.edit(f"{retry_message} ({attempt + 1}/{MAX_RETRIES})")
                else:
                    return None, None

    download_path, download_time = await handle_download(data["direct_link"], data["file_name"], "Retrying download from primary server...")

    if not download_path:
        await hm.edit("Trying download from secondary server...")
        download_path, download_time = await handle_download(data["link"], data["file_name"], "Retrying download from secondary server...")

    if not download_path:
        return await hm.edit("Download failed after multiple attempts from both servers.")

    file_size = os.path.getsize(download_path)

    start_upload_time = time.time()
    try:
        file = await bot.send_file(
            PRIVATE_CHAT_ID,
            file=download_path,
            thumb=thumbnail if thumbnail else None,
            progress_callback=progress_bar,
            caption=f"""
**Title** - **{data["file_name"]}**

**Size**: **{get_formatted_size(file_size)}**
**Downloaded in**: `{convert_seconds(download_time)}`
**Uploaded in**: `{convert_seconds(time.time() - start_upload_time)}`
**Uploaded by**: {sender_id}

**Join @BillaSpace**
""",
            supports_streaming=True,
            spoiler=True,
        )
        os.remove(download_path)

    except telethon.errors.rpcerrorlist.WebpageCurlFailedError:
        download = await download_file(
            data["direct_link"], data["file_name"], progress_bar
        )
        if not download:
            return await hm.edit(
                f"Sorry! Download failed, but you can download it from [here]({data['direct_link']}).",
                parse_mode="markdown",
            )
        file = await bot.send_file(
            PRIVATE_CHAT_ID,
            download,
            caption=f"""
**Title** - **{data["file_name"]}**

**Size**: **{get_formatted_size(file_size)}**
**Downloaded in**: `{convert_seconds(download_time)}`
**Uploaded in**: `{convert_seconds(time.time() - start_upload_time)}`
**Uploaded by**: {sender_id}

**Join @AlphaBotz**
""",
            progress_callback=progress_bar,
            thumb=thumbnail if thumbnail else None,
            supports_streaming=True,
            spoiler=True,
        )
        try:
            os.unlink(download)
        except Exception as e:
            print(e)
    except Exception:
        return await hm.edit(
            f"Sorry! Download it from [here]({data['link']}).",
            parse_mode="markdown",
        )

    try:
        os.unlink(download_path)
    except Exception as e:
        pass
    try:
        await hm.delete()
    except Exception as e:
        print(e)

    if shorturl:
        await file_cache_collection.update_one(
            {"_id": shorturl},
            {"$set": {"file_id": file.id}},
            upsert=True
        )
    if file:
        await file_cache_collection.update_one(
            {"_id": uuid},
            {"$set": {"file_id": file.id}},
            upsert=True
        )

        await bot(
            ForwardMessagesRequest(
                from_peer=PRIVATE_CHAT_ID,
                id=[file.id],
                to_peer=m.chat.id,
                top_msg_id=m.id,
                drop_author=True,
                noforwards=False,
                background=True,
                drop_media_captions=False,
                with_my_score=True,
            )
        )

@bot.on(events.NewMessage(pattern='/stats', incoming=True))
async def stats_command(event):
    if event.sender_id not in dev_users:
        return await event.reply("You are not authorized to use this command.")
    total_users = await user_tokens_collection.count_documents({})
    uptime_str = uptime()
    await event.reply(f"Total Users: {total_users}\nUptime: {uptime_str}")

def uptime():
    uptime_seconds = int(time.time() - start_time)
    return str(timedelta(seconds=uptime_seconds))

@bot.on(events.NewMessage(pattern='/broadcast', incoming=True))
async def broadcast_command(event):
    if event.sender_id not in dev_users:
        return await event.reply("You are not authorized to use this command.")

    await event.reply("Broadcast starting...")

    users_cursor = user_tokens_collection.find({}, {"user_id": 1})
    users = [user['user_id'] for user in await users_cursor.to_list(length=None)]

    success_count = 0
    blocked_count = 0
    deleted_count = 0

    if event.is_reply:
        reply_message = await event.get_reply_message()
        for user_id in users:
            try:
                await bot.forward_messages(int(user_id), reply_message)
                success_count += 1
            except UserBlockedError:
                blocked_count += 1
            except UserDeactivatedError:
                deleted_count += 1
            except Exception:
                pass
    else:
        message = event.message.message.split('/broadcast ', 1)[-1]
        for user_id in users:
            try:
                await bot.send_message(int(user_id), message)
                success_count += 1
            except UserBlockedError:
                blocked_count += 1
            except UserDeactivatedError:
                deleted_count += 1
            except Exception:
                pass

    await event.reply(f"Broadcast sent to all users.\n\nSuccessfully: {success_count}\nBlocked: {blocked_count}\nDeleted: {deleted_count}")

@bot.on(events.NewMessage(pattern='/apr (\d+)', incoming=True))
async def add_pr_user(event):
    if event.sender_id not in dev_users:
        return await event.reply("You are not authorized to use this command.")

    user_id = int(event.pattern_match.group(1))
    pr_user = await premium_users_collection.find_one({"user_id": str(user_id)})
    if pr_user:
        return await event.reply("User is already a premium user.")

    await premium_users_collection.insert_one({"user_id": str(user_id)})
    await event.reply(f"User {user_id} has been added to premium users.")

@bot.on(events.NewMessage(pattern='/rpr (\d+)', incoming=True))
async def remove_pr_user(event):
    if event.sender_id not in dev_users:
        return await event.reply("You are not authorized to use this command.")

    user_id = int(event.pattern_match.group(1))
    pr_user = await premium_users_collection.find_one({"user_id": str(user_id)})
    if not pr_user:
        return await event.reply("User is not a premium user.")

    await premium_users_collection.delete_one({"user_id": str(user_id)})
    await event.reply(f"User {user_id} has been removed from premium users.")

import string
import random

def generate_code(length: int) -> str:
    prefix = "DELTA-"
    alpha_numeric = string.ascii_letters + string.digits
    code = prefix + ''.join(random.choices(alpha_numeric, k=length))
    return code

@bot.on(events.NewMessage(pattern='/code (\d+)', incoming=True))
async def generate_gift_code(event):
    if event.sender_id not in dev_users:
        return await event.reply("You are not authorized to use this command.")

    hours = int(event.pattern_match.group(1))
    code = generate_code(8)
    expiry_time = int(time.time()) + (hours * 3600)

    await gift_codes_collection.update_one(
        {"_id": code},
        {"$set": {"expiry_time": expiry_time, "redeemed": False}},
        upsert=True
    )

    await event.reply(f"Gift code `{code}` generated successfully for {hours} hours.")

@bot.on(events.NewMessage(pattern='/redeem (.+)', incoming=True))
async def redeem_gift_code(event):
    code = event.pattern_match.group(1)

    code_doc = await gift_codes_collection.find_one({"_id": code})
    if not code_doc or code_doc["expiry_time"] < int(time.time()):
        return await event.reply("Invalid or expired code.")

    if code_doc["redeemed"]:
        return await event.reply("This code has already been redeemed.")

    expiry_seconds = code_doc["expiry_time"] - int(time.time())
    await premium_users_collection.insert_one({"user_id": str(event.sender_id)})
    await gift_codes_collection.update_one(
        {"_id": code},
        {"$set": {"redeemed": True}}
    )

    await event.reply(f"Code `{code}` redeemed successfully. You are now a premium user.")

@bot.on(events.NewMessage(pattern='/prlist', incoming=True))
async def show_pr_users(event):
    if event.sender_id not in dev_users:
        return await event.reply("You are not authorized to use this command.")

    pr_users_cursor = premium_users_collection.find({}, {"user_id": 1})
    pr_users = [user["user_id"] async for user in pr_users_cursor]

    if not pr_users:
        return await event.reply("No users are currently in the premium users list.")

    users_list = "\n".join(str(user_id) for user_id in pr_users)
    await event.reply(f"Premium users:\n{users_list}")

bot.start(bot_token=BOT_TOKEN)
print('bot started ')
bot.run_until_disconnected()
