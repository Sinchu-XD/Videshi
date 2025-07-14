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

    # Try single file first
    try:
        data = await get_file_by_id(file_ref_id)
    except InvalidId:
        data = None

    # If not found, try bulk album
    if not data:
        try:
            data = await get_bulk_file_by_id(file_ref_id)
        except InvalidId:
            data = None

    if not data:
        try:
            return await message.reply_text("❌ File not found or expired link.")
        except UserIsBlocked:
            print(f"[BLOCKED] Can't reply to {user_id}: User has blocked the bot.")
            return

    # Single file restore
    if "chat_id" in data:
        # Log
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

        # Get and send
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

            # Auto-delete
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

    # Bulk album restore
    elif "files" in data:
        files = data["files"]
        count = len(files)

        # Log
        try:
            mention = f"[{user.first_name}](tg://user?id={user.id})"
            await bot.send_message(
                Config.LOG_CHANNEL_ID,
                f"#BULK_RESTORE\n👤 **User:** {mention}\n"
                f"📁 **Requested Bulk ID:** `{file_ref_id}`\n"
                f"📦 **Files Count:** {count}",
                parse_mode="md"
            )
        except Exception as e:
            print(f"[LOG ERROR] {e}")

        # Notify user
        await message.reply_text(
            f"📦 Found {count} files. Sending them one by one..."
        )

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
                    await message.reply_text("❌ One file in album not found.")

                # Optional: auto-delete each file after 10 min
                await asyncio.sleep(600)
                try:
                    if sent:
                        await sent.delete()
                except Exception as e:
                    print(f"[AUTO DELETE ERROR] {e}")

                # Short pause to avoid flood
                await asyncio.sleep(1)

            except Exception as e:
                print(f"[BULK RESTORE ERROR] {e}")
                continue

