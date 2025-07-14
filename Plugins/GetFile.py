from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserIsBlocked
from Config import Config
from Bot import bot
from Database import get_file_by_id, get_bulk_file_by_id, add_user
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
        data = None

    if not data:
        try:
            data = await get_bulk_file_by_id(file_ref_id)
        except InvalidId:
            data = None

    if not data:
        try:
            return await message.reply_text("❌ File not found or expired link.")
        except UserIsBlocked:
            return

    if "chat_id" in data:
        try:
            original_msg = await bot.get_messages(data["chat_id"], data["message_id"])
            doc = original_msg.document
            vid = original_msg.video
            photo = original_msg.photo

            sent = None

            if doc:
                sent = await message.reply_document(
                    document=doc.file_id,
                    caption="📂 Sending your file...\n\nThis file will auto-delete in 10 minutes.",
                    protect_content=True
                )
            elif vid:
                sent = await message.reply_video(
                    video=vid.file_id,
                    caption="📂 Sending your file...\n\nThis file will auto-delete in 10 minutes.",
                    protect_content=True
                )
            elif photo:
                sent = await message.reply_photo(
                    photo=photo.file_id,
                    caption="📂 Sending your file...\n\nThis file will auto-delete in 10 minutes.",
                    protect_content=True
                )
            else:
                return await message.reply_text("❌ File not found or deleted.")

            await asyncio.sleep(600)
            try:
                await sent.delete()
            except:
                pass

        except Exception as e:
            await message.reply_text("⚠️ Failed to send the file.")

    elif "files" in data:
        files = data["files"]
        await message.reply_text(f"📦 Found {len(files)} files. Sending them one by one...")

        for file in files:
            try:
                original_msg = await bot.get_messages(file["chat_id"], file["message_id"])
                doc = original_msg.document
                vid = original_msg.video
                photo = original_msg.photo

                sent = None

                if doc:
                    sent = await message.reply_document(
                        document=doc.file_id,
                        protect_content=True
                    )
                elif vid:
                    sent = await message.reply_video(
                        video=vid.file_id,
                        protect_content=True
                    )
                elif photo:
                    sent = await message.reply_photo(
                        photo=photo.file_id,
                        protect_content=True
                    )
                else:
                    await message.reply_text("❌ One file not found.")

                await asyncio.sleep(600)
                try:
                    if sent:
                        await sent.delete()
                except:
                    pass

                await asyncio.sleep(1)

            except Exception as e:
                continue
