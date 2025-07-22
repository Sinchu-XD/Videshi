from Config import Config
from Bot import bot
from pyrogram import filters, Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from Database import get_channels, get_sudo_list, get_main_channel, get_file_by_id
from functools import wraps
import asyncio

# 🔹 Return list of channels the user has NOT joined
async def check_subscription(client: Client, user_id: int) -> list:
    channels = await get_channels()
    if not channels:
        return []

    not_joined = []

    for channel in channels:
        try:
            if not channel.startswith("@"):
                channel = f"@{channel}"
            member = await client.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked"):
                not_joined.append(channel)
        except Exception:
            not_joined.append(channel)

    return not_joined

# 🔹 Forward file after verification
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
    except Exception as e:
        await client.send_message(chat_id, f"⚠️ Failed to send the file. Error: {e}")

# 🔹 Decorator to enforce subscription
def subscription_required():
    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: Message):
            user_id = message.from_user.id
            not_joined = await check_subscription(client, user_id)

            if not not_joined:
                return await func(client, message)

            file_ref_id = None
            if message.text and message.text.startswith("/start "):
                file_ref_id = message.text.split(" ", 1)[1]

            buttons = [
                [InlineKeyboardButton(f"📡 Join {ch}", url=f"https://t.me/{ch.lstrip('@')}")]
                for ch in not_joined
            ]
            buttons.append([
                InlineKeyboardButton("✅ I Joined", callback_data=f"check_join_{file_ref_id or 'none'}")
            ])

            await message.reply_text(
                "📥 **Please join all required channels to use this bot**:\n\nवीडियो प्राप्त करने के लिए नीचे दिए हुए सभी चैनल में जुड़ें, फिर **I JOINED** दबाएं।",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        return wrapper
    return decorator

# 🔹 Callback to recheck after "I Joined"
@bot.on_callback_query(filters.regex(r"check_join_(.+)"))
async def recheck_subscription(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    file_ref_id = data.split("_", 2)[2] if "_" in data else None

    not_joined = await check_subscription(client, user_id)

    if not not_joined:
        main_channel = await get_main_channel()
        keyboard = []
        if main_channel:
            keyboard.append([InlineKeyboardButton("🏠 Main Channel", url=f"https://t.me/{main_channel}")])

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
            """,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        if file_ref_id and file_ref_id != "none":
            await send_file_by_ref_id(client, callback_query.message.chat.id, file_ref_id)
    else:
        buttons = [
            [InlineKeyboardButton(f"📡 Join {ch}", url=f"https://t.me/{ch.lstrip('@')}")]
            for ch in not_joined
        ]
        buttons.append([InlineKeyboardButton("✅ I Joined", callback_data=f"check_join_{file_ref_id or 'none'}")])

        await callback_query.message.edit_text(
            "❌ You're still not subscribed to all required channels. Please join them and tap 'I Joined' again.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# 🔹 (Optional) Message cleaner for later use
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
        
