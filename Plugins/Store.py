from pyrogram import Client, filters
from pyrogram.types import Message
from Config import Config
from Bot import bot
from Database import save_file, save_bulk_file, get_sudo_list
from collections import defaultdict
import asyncio

media_groups = defaultdict(list)
media_group_tasks = {}

MAX_FILE_SIZE_MB = 4096  # 4GB

async def is_admin(uid: int) -> bool:
    sudo_users = await get_sudo_list()
    return uid == Config.OWNER_ID or uid in sudo_users

@bot.on_message(filters.private & filters.media)
async def handle_bulk_upload(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply_text("❌ You are not authorized to save files.")

    media = message.document or message.video or message.photo
    if not media:
        return await message.reply_text("❌ Please send a valid file.")

    file_type = (
        "document" if message.document else
        "video" if message.video else
        "photo"
    )
    file_size = (
        message.document.file_size if message.document else
        message.video.file_size if message.video else
        message.photo.file_size if message.photo else
        0
    )

    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return await message.reply_text(f"❌ File too large! Max is {MAX_FILE_SIZE_MB} MB.")

    mgid = message.media_group_id

    if mgid:
        media_groups[mgid].append({
            "chat_id": message.chat.id,
            "message_id": message.id,
            "file_type": file_type
        })

        # If no task yet, start a delayed save task
        if mgid not in media_group_tasks:
            async def delayed_save():
                await asyncio.sleep(5)  # wait for user to finish sending album
                files = media_groups.pop(mgid, [])
                if len(files) >= 2:
                    ref_id = await save_bulk_file(
                        user_id=message.from_user.id,
                        media_group_id=mgid,
                        files=files
                    )
                    link = f"https://t.me/{Config.BOT_USERNAME}?start={ref_id}"
                    await message.reply_text(
                        f"✅ Bulk files saved!\n\n🔗 Link: {link}\n📦 Files: {len(files)}"
                    )
                else:
                    # If only one file, save as single
                    if files:
                        file = files[0]
                        ref_id = await save_file(
                            user_id=message.from_user.id,
                            chat_id=file["chat_id"],
                            message_id=file["message_id"],
                            file_type=file["file_type"]
                        )
                        link = f"https://t.me/{Config.BOT_USERNAME}?start={ref_id}"
                        await message.reply_text(
                            f"✅ File saved!\n\n🔗 Link: {link}"
                        )
                media_group_tasks.pop(mgid, None)

            media_group_tasks[mgid] = asyncio.create_task(delayed_save())

    else:
        ref_id = await save_file(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            message_id=message.id,
            file_type=file_type
        )
        link = f"https://t.me/{Config.BOT_USERNAME}?start={ref_id}"
        await message.reply_text(
            f"✅ File saved!\n\n🔗 Link: {link}"
        )
