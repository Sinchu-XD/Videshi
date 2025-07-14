from pyrogram import Client, filters
from pyrogram.types import Message
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
    file_ref_id = message.text.split(" ", 1)[1]
    await add_user(user.id, user.first_name, user.username)

    data = None
    try:
        data = await get_file_by_id(file_ref_id)
    except InvalidId:
        pass

    if not data:
        try:
            data = await get_bulk_file_by_id(file_ref_id)
        except InvalidId:
            pass

    if not data:
        return await message.reply_text("❌ File not found or invalid link.")

    if "files" in data:
        files = data["files"]
        await message.reply_text(f"📦 Found {len(files)} files. Sending them one by one...")

        for idx, file in enumerate(files, start=1):
            try:
                original_msg = await bot.get_messages(file["chat_id"], file["message_id"])
                sent = None

                if original_msg.document:
                    sent = await bot.send_document(
                        chat_id=message.chat.id,
                        document=original_msg.document.file_id,
                        caption=f"📦 File {idx}/{len(files)}",
                        protect_content=True
                    )
                elif original_msg.video:
                    sent = await bot.send_video(
                        chat_id=message.chat.id,
                        video=original_msg.video.file_id,
                        caption=f"📦 File {idx}/{len(files)}",
                        protect_content=True
                    )
                elif original_msg.photo:
                    sent = await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=original_msg.photo.file_id,
                        caption=f"📦 File {idx}/{len(files)}",
                        protect_content=True
                    )
                else:
                    await bot.send_message(
                        chat_id=message.chat.id,
                        text=f"❌ File {idx} not found or invalid."
                    )
                    continue

                await asyncio.sleep(600)
                if sent:
                    await sent.delete()

                await asyncio.sleep(1)

            except Exception as e:
                print(f"[RESTORE ERROR] File {idx}: {e}")
                await bot.send_message(
                    chat_id=message.chat.id,
                    text=f"⚠️ Failed to send file {idx}."
                )

    else:
        try:
            original_msg = await bot.get_messages(data["chat_id"], data["message_id"])
            sent = None

            if original_msg.document:
                sent = await message.reply_document(
                    document=original_msg.document.file_id,
                    protect_content=True
                )
            elif original_msg.video:
                sent = await message.reply_video(
                    video=original_msg.video.file_id,
                    protect_content=True
                )
            elif original_msg.photo:
                sent = await message.reply_photo(
                    photo=original_msg.photo.file_id,
                    protect_content=True
                )
            else:
                return await message.reply_text("❌ File not found.")

            await asyncio.sleep(600)
            if sent:
                await sent.delete()

        except Exception as e:
            print(f"[RESTORE ERROR] Single file: {e}")
            await message.reply_text("⚠️ Failed to send the file.")
