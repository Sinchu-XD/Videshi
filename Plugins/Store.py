from pyrogram import Client, filters
from pyrogram.types import Message
from Config import Config
from Bot import bot
from Database import save_file, save_bulk_file, get_sudo_list
from collections import defaultdict
import asyncio

media_groups = defaultdict(list)

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

        await asyncio.sleep(2)

        files = media_groups.get(mgid)
        if files and len(files) >= 2:
            ref_id = await save_bulk_file(
                user_id=message.from_user.id,
                media_group_id=mgid,
                files=files
            )
            link = f"https://t.me/{Config.BOT_USERNAME}?start={ref_id}"
            await message.reply_text(
                f"✅ Bulk files saved!\n\n🔗 Link: {link}\n📦 Files: {len(files)}"
            )
            media_groups.pop(mgid, None)

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
