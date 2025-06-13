from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserIsBlocked
from Config import Config
from Bot import bot
from Database import get_file_by_id, add_user
from Decorators import subscription_required
from bson.errors import InvalidId
import asyncio

@bot.on_message(filters.command("start") & filters.regex(r"^/start\s(.+)"))
@subscription_required()
async def start_link_restore(client: Client, message: Message):
    user = message.from_user
    user_id = user.id
    file_ref_id = message.text.split(" ", 1)[1]

    await add_user(user.id, user.first_name, user.username)

    try:
        data = await get_file_by_id(file_ref_id)
    except InvalidId:
        try:
            return await message.reply_text("❌ Invalid or expired file link.")
        except UserIsBlocked:
            print(f"[BLOCKED] Can't reply to {user_id}: User has blocked the bot.")
            return

    if not data:
        try:
            return await message.reply_text("❌ File not found or deleted.")
        except UserIsBlocked:
            print(f"[BLOCKED] Can't reply to {user_id}: User has blocked the bot.")
            return

    try:
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        await bot.send_message(
            Config.LOG_CHANNEL_ID,
            f"#RESTORE\n👤 **User:** {mention}\n"
            f"📁 **Requested File ID:** `{file_ref_id}`\n"
            f"📦 **Type:** {data['file_type']}",
            parse_mode="md"
        )
    except Exception as e:
        print(f"[LOG ERROR] {e}")

    try:
        original_msg = await bot.get_messages(data["chat_id"], data["message_id"])
        sent = await message.reply_cached_media(
            media=original_msg.document or original_msg.video or original_msg.photo,
            caption="📂 Sending your file...\n\nThis file will auto-delete in 10 minutes.",
            protect_content=True
        )

        await asyncio.sleep(600)
        try:
            await sent.delete()
        except Exception as e:
            print(f"[AUTO DELETE ERROR] {e}")

    except UserIsBlocked:
        print(f"[BLOCKED] Cannot send file to {user_id}: User has blocked the bot.")
    except Exception as e:
        print(f"[RESTORE ERROR] {e}")
        try:
            await message.reply_text("⚠️ Failed to send the file. Try again later.")
        except UserIsBlocked:
            print(f"[BLOCKED] Can't reply to {user_id}: User has blocked the bot.")
          
