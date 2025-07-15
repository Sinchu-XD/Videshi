from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
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
    file_ref_id = message.text.split(" ", 1)[1].strip()

    await add_user(user.id, user.first_name, user.username)

    # Try single file first
    data = None
    try:
        data = await get_file_by_id(file_ref_id)
    except InvalidId:
        pass

    # If not found, try bulk
    if not data:
        try:
            data = await get_bulk_file_by_id(file_ref_id)
        except InvalidId:
            pass

    if not data:
        return await message.reply_text("❌ File not found or invalid link.")

    # Prepare join button
    join_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Mega Channel", url="https://t.me/+2J7I2uD7Xuo3M2Fl")]
    ])

    async def auto_delete(sent_msg, delay=600):
        await asyncio.sleep(delay)
        try:
            await sent_msg.delete()
        except Exception as e:
            print(f"[AUTO DELETE ERROR] {e}")

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
                        protect_content=True,
                        reply_markup=join_button
                    )
                elif original_msg.video:
                    sent = await bot.send_video(
                        chat_id=message.chat.id,
                        video=original_msg.video.file_id,
                        caption=f"📦 File {idx}/{len(files)}",
                        protect_content=True,
                        reply_markup=join_button
                    )
                elif original_msg.photo:
                    sent = await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=original_msg.photo.file_id,
                        caption=f"📦 File {idx}/{len(files)}",
                        protect_content=True,
                        reply_markup=join_button
                    )
                else:
                    await message.reply_text(f"❌ File {idx} has no valid media.")
                    continue

                asyncio.create_task(auto_delete(sent, 600))
                await asyncio.sleep(1)

            except Exception as e:
                print(f"[RESTORE ERROR] File {idx}: {e}")
                await message.reply_text(f"⚠️ Failed to send file {idx}.")

    else:
        try:
            original_msg = await bot.get_messages(data["chat_id"], data["message_id"])
            sent = None

            if original_msg.document:
                sent = await bot.send_document(
                    chat_id=message.chat.id,
                    document=original_msg.document.file_id,
                    protect_content=True,
                    reply_markup=join_button
                )
            elif original_msg.video:
                sent = await bot.send_video(
                    chat_id=message.chat.id,
                    video=original_msg.video.file_id,
                    protect_content=True,
                    reply_markup=join_button
                )
            elif original_msg.photo:
                sent = await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=original_msg.photo.file_id,
                    protect_content=True,
                    reply_markup=join_button
                )
            else:
                return await message.reply_text("❌ File not found or invalid media.")

            asyncio.create_task(auto_delete(sent, 600))

        except Exception as e:
            print(f"[RESTORE ERROR] Single file: {e}")
            await message.reply_text("⚠️ Failed to send the file.")
            
