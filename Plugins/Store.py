from pyrogram import Client, filters
from pyrogram.types import Message
from Config import Config
from Bot import bot
from Database import save_file, get_sudo_list
from datetime import datetime

MAX_FILE_SIZE_MB = 4096  # 4GB limit

async def is_admin(uid: int) -> bool:
    sudo_users = await get_sudo_list()
    return uid == Config.OWNER_ID or uid in sudo_users


@bot.on_message(filters.private & filters.media)
async def handle_file(client: Client, message: Message):
    media = message.document or message.video or message.audio or message.photo

    if not media:
        return await message.reply_text("❌ Please send a photo, video, or document.")

    # Get file type and size
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

    # Save to DB
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

    # Log to admin/log channel
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
        print(f"[LOG ERROR] Failed to log upload: {e}")
      
