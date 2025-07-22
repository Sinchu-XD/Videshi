import time
import asyncio
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Config import Config
from Bot import bot
from Database import add_user, get_sudo_list
from Database import add_blocked_user, get_blocked_user, remove_blocked_user

user_command_times = defaultdict(list)
VIOLATION_WINDOW = 5
BLOCK_DURATION = 10 * 60

async def is_admin(uid: int) -> bool:
    sudo_users = await get_sudo_list()
    return uid == Config.OWNER_ID or uid in sudo_users

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    user = message.from_user
    now = time.time()

    try:
        unblock_time = await get_blocked_user(user_id)
        if unblock_time:
            if now >= unblock_time:
                await remove_blocked_user(user_id)
                user_command_times[user_id].clear()
                try:
                    msg = await message.reply_text(
                        "**✅ You are now unblocked. Please avoid spamming commands.**\n\n"
                        "**✅ अब आप अनब्लॉक हो चुके हैं। कृपया बार-बार कमांड भेजना बंद करें।**"
                    )
                    await asyncio.sleep(60)
                    await msg.delete()
                except:
                    pass
            else:
                wait = int((unblock_time - now) / 60)
                msg = await message.reply_text(
                    f"**⛔ You are blocked for {wait} more minutes due to spamming.**\n\n"
                    f"**⛔ आप {wait} मिनट के लिए ब्लॉक हैं क्योंकि आपने बार-बार कमांड भेजी।**"
                )
                await asyncio.sleep(60)
                await msg.delete()
                return

        user_command_times[user_id].append(now)
        user_command_times[user_id] = [
            t for t in user_command_times[user_id] if now - t <= VIOLATION_WINDOW
        ]

        if len(user_command_times[user_id]) == 3:
            msg = await message.reply_text(
                "⚠️ **Stop spamming commands! One more and you will be blocked for 10 minutes.**\n\n"
                "⚠️ **बार-बार कमांड मत भेजो! अगली बार 10 मिनट के लिए ब्लॉक हो जाओगे।**"
            )
            await asyncio.sleep(60)
            await msg.delete()
        elif len(user_command_times[user_id]) > 3:
            await add_blocked_user(user_id, BLOCK_DURATION)
            user_command_times[user_id].clear()
            msg = await message.reply_text(
                "⛔ **You are now blocked for 10 minutes due to spamming.**\n\n"
                "⛔ **आप 10 मिनट के लिए ब्लॉक हो चुके हैं क्योंकि आपने बार-बार कमांड भेजी।**"
            )
            await asyncio.sleep(60)
            await msg.delete()

            mention = f"[{user.first_name}](tg://user?id={user.id})"
            try:
                await bot.send_message(
                    Config.LOG_CHANNEL_ID,
                    f"🚫 BLOCKED\n👤 User: {mention} (`{user.id}`)\n📛 Reason: Spammed `/start` more than 3 times in {VIOLATION_WINDOW} seconds.",
                )
            except:
                pass
            return

        await add_user(user.id, user.first_name, user.username)
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        try:
            await bot.send_message(
                Config.LOG_CHANNEL_ID,
                f"START\n👤 User: {mention}\n📩 Started the bot.",
            )
        except:
            pass

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Main Channel", url="https://t.me/+N-ujk8NAZxE0ZDQx")],
            [InlineKeyboardButton("How To Use Bot", url="https://t.me/StreeUses/3")]
        ])

        if await is_admin(user_id):
            msg = await message.reply_text(
                "👋 Welcome Admin!\n\n📤 Send any file to convert into a sharable link."
            )
        else:
            msg = await message.reply_text(
                "•  **How To Use Bot Tutorial Watch Here :-**\n\n"
                "• **बॉट ट्यूटोरियल का उपयोग कैसे करें यहां क्लिक करके देखें:**\n👇🏻👇🏻👇🏻",
                reply_markup=keyboard
            )

        await asyncio.sleep(60)
        await msg.delete()

    except Exception as e:
        import traceback
        print("Unhandled error in /start command:", traceback.format_exc())
              
