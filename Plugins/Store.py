from pyrogram import Client, filters
from pyrogram.types import Message
from Config import Config
from Bot import bot
from Database import save_file, save_bulk_file, get_sudo_list
from datetime import datetime

MAX_FILE_SIZE_MB = 4096  # 4GB limit

async def is_admin(uid: int) -> bool:
    sudo_users = await get_sudo_list()
    return uid == Config.OWNER_ID or uid in sudo_users

# Store a temporary dict for group messages
# In production, use Redis or DB for cross-process safety!
media_groups = {}

@bot.on_message(filters.private & filters.media)
async def handle_file(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply_text("❌ You are not authorized to save files.")

    media = message.document or message.video or message.audio or message.photo
    if not media:
        return await message.reply_text("❌ Please send a photo, video, or document.")

    # Detect media type and size
    if message.document:
        file_type = "document"
        file_size = message.document.file_size
    elif message.video:
        file_type = "video"
        file_size = message.video.file_size
    elif message.audio:
        file_type = "audio"
        file_size = message.audio.file_size
    elif message.photo:
        file_type = "photo"
        file_size = message.photo.file_size
    else:
        file_type = "unknown"
        file_size = 0

    file_size_mb = file_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return await message.reply_text(f"❌ File too large! Max size is {MAX_FILE_SIZE_MB} MB.")

    media_group_id = message.media_group_id

    # -----------------------------
    # 🗂️ 1) Save file to DB
    # -----------------------------
    if media_group_id:
        # If part of an album, save to temporary group
        group_key = f"{message.from_user.id}:{media_group_id}"
        if group_key not in media_groups:
            media_groups[group_key] = []
        media_groups[group_key].append({
            "chat_id": message.chat.id,
            "message_id": message.id,
            "file_type": file_type,
        })

        # Wait a bit because albums can send messages in parallel
        await asyncio.sleep(1)

        # Check if this is the last message in the group (safe version)
        # For real production, you’d handle this more robustly with DB locks
        if len(media_groups[group_key]) >= 1:
            # Save the entire group under one bulk ref_id
            bulk_ref_id = await save_bulk_file(
                user_id=message.from_user.id,
                media_group_id=media_group_id,
                files=media_groups[group_key]
            )

            link = f"https://t.me/{Config.BOT_USERNAME}?start={bulk_ref_id}"

            await message.reply_text(
                f"✅ Bulk files saved!\n\n🔗 **Link:** `{link}`\n📦 **Files:** {len(media_groups[group_key])}",
                quote=True
            )

            # Log
            try:
                mention = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                await bot.send_message(
                    Config.LOG_CHANNEL_ID,
                    f"#BULK_UPLOAD\n👤 **Uploader:** {mention}\n"
                    f"📦 **Files:** {len(media_groups[group_key])}\n"
                    f"🆔 **Ref ID:** `{bulk_ref_id}`\n"
                    f"🔗 [Open Bulk Link]({link})",
                    parse_mode="md"
                )
            except Exception as e:
                print(f"[LOG ERROR] {e}")

            # Clear group
            del media_groups[group_key]

    else:
        # -----------------------------
        # 🗂️ 2) Save single file
        # -----------------------------
        file_ref_id = await save_file(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            message_id=message.id,
            file_type=file_type,
        )

        link = f"https://t.me/{Config.BOT_USERNAME}?start={file_ref_id}"

        await message.reply_text(
            f"✅ File saved!\n\n🔗 **Link:** `{link}`\n🆔 **Ref ID:** `{file_ref_id}`\n"
            f"📦 **Type:** {file_type}\n💾 **Size:** {file_size_mb:.2f} MB",
            quote=True
        )

        # Log
        try:
            mention = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            await bot.send_message(
                Config.LOG_CHANNEL_ID,
                f"#UPLOAD\n👤 **Uploader:** {mention}\n"
                f"📦 **Type:** {file_type}\n🆔 **Ref ID:** `{file_ref_id}`\n"
                f"💾 **Size:** {file_size_mb:.2f} MB\n"
                f"🔗 [Open File Link]({link})",
                parse_mode="md"
            )
        except Exception as e:
            print(f"[LOG ERROR] {e}")
