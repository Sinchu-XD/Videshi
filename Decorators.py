from Config import Config
from Bot import bot
from pyrogram import filters, Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from Database import get_channels, get_sudo_list, get_main_channel, get_file_by_id
from functools import wraps
import asyncio

async def check_subscription(client: Client, user_id: int) -> bool:
    channels = await get_channels()
    if not channels:
        return True

    for channel in channels:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except Exception as e:
            print(f"Error checking subscription for channel {channel}: {e}")
            return False

    return True


async def send_file_by_ref_id(client: Client, chat_id: int, file_ref_id: str):
    data = await get_file_by_id(file_ref_id)
    if not data:
        await client.send_message(chat_id, "❌ File not found or deleted.")
        return

    try:
        original_msg = await bot.get_messages(data["chat_id"], data["message_id"])
        sent = await client.send_document(
            chat_id,
            document=original_msg.document if data["file_type"] == "document" else original_msg.video,
            caption="📂 Sending your video...\n\nThis video will auto-delete in 20 minutes.",
            protect_content=True
        )
        await asyncio.sleep(1200)
        try:
            await sent.delete()
        except Exception as e:
            print(f"Error deleting sent file: {e}")
            pass
    except Exception as e:
        await client.send_message(chat_id, f"⚠️ Failed to send the file. Error: {e}")


def subscription_required():
    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: Message):
            user_id = message.from_user.id
            if await check_subscription(client, user_id):
                return await func(client, message)

            channels = await get_channels()
            main_channel = await get_main_channel()
            buttons = [
                [InlineKeyboardButton(f"📡 Join @{ch}", url=f"https://t.me/{ch}")]
                for ch in channels
            ]

            file_ref_id = None
            if message.text and message.text.startswith("/start "):
                file_ref_id = message.text.split(" ", 1)[1]

            buttons.append([
                InlineKeyboardButton("✅ I Joined", callback_data=f"check_join_{file_ref_id or 'none'}")
            ])

            await message.reply_text(
                "📥** Please join all required channels to use this bot**:\n\n वीडियो प्राप्त करने के लिए नीचे दिए हुए तीनो चैनल पे क्लिक करके जुड़ें करो उसके बाद **I JOINED** बटन पर क्लिक करें",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        return wrapper
    return decorator


@bot.on_callback_query(filters.regex(r"check_join_(.+)"))
async def recheck_subscription(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    file_ref_id = data.split("_", 2)[2] if "_" in data else None

    main_channel = await get_main_channel()
    keyboard = []
    if main_channel:
        keyboard.append([InlineKeyboardButton("🏠 Main Channel", url=f"https://t.me/{main_channel}")])

    if await check_subscription(client, user_id):
        await callback_query.message.edit_text(
            """
• You're Successfully Verified.
• Now You Can Use Bot Without Any Interrupt.
• Please Click On Main Channel For All 18+ Contents.
• You Get Many Videos There, Only You Have To Click On Link Which One You Want.

• आपका सफलतापूर्वक सत्यापन हो गया है।
• अब आप बिना किसी रुकावट के बॉट का उपयोग कर सकते हैं।
• कृपया सभी 18+ वीडियो के लिए Main Channel पर क्लिक करें |
• आपको वहां कई वीडियो मिलेंगे, आपको उस लिंक पर क्लिक करना है जो आप देखना चाहते हैं |
👇🏻👇🏻👇🏻
            """,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        if file_ref_id and file_ref_id != "none":
            await send_file_by_ref_id(client, callback_query.message.chat.id, file_ref_id)
    else:
        await callback_query.answer("🚫 You haven't joined all channels yet.", show_alert=True)

    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"Error deleting callback message: {e}")


async def delete_messages(user_message: Message, bot_message: Message, delay=5):
    await asyncio.sleep(delay)
    try:
        await user_message.delete()
    except Exception as e:
        print(f"Error deleting user message: {e}")
    try:
        await bot_message.delete()
    except Exception as e:
        print(f"Error deleting bot message: {e}")
