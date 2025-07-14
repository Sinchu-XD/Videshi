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
        await message.reply_text(f"📦 Found {len(files)} files. Sending them one by one..")
        for file in files:
            try:
                orig = await bot.get_messages(file["chat_id"], file["message_id"])
                sent = None

                if orig.document:
                    sent = await message.reply_document(
                        document=orig.document.file_id,
                        protect_content=True
                    )
                elif orig.video:
                    sent = await message.reply_video(
                        video=orig.video.file_id,
                        protect_content=True
                    )
                elif orig.photo:
                    sent = await message.reply_photo(
                        photo=orig.photo.file_id,
                        protect_content=True
                    )

                await asyncio.sleep(600)  # 10 min auto delete
                if sent:
                    await sent.delete()

                await asyncio.sleep(1)  # tiny delay between files

            except Exception as e:
                print(f"[RESTORE ERROR] {e}")
                continue

    else:
        try:
            orig = await bot.get_messages(data["chat_id"], data["message_id"])
            sent = None

            if orig.document:
                sent = await message.reply_document(
                    document=orig.document.file_id,
                    protect_content=True
                )
            elif orig.video:
                sent = await message.reply_video(
                    video=orig.video.file_id,
                    protect_content=True
                )
            elif orig.photo:
                sent = await message.reply_photo(
                    photo=orig.photo.file_id,
                    protect_content=True
                )

            await asyncio.sleep(600)
            if sent:
                await sent.delete()

        except Exception as e:
            print(f"[RESTORE ERROR] {e}")
            await message.reply_text("⚠️ Failed to send the file.")
            
