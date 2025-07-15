from pyrogram import Client, filters
from pyrogram.types import Message
from Bot import bot
from Config import Config
from Database import get_all_users, get_sudo_list
import asyncio

async def is_admin(uid: int) -> bool:
    sudo_users = await get_sudo_list()
    return uid == Config.OWNER_ID or uid in sudo_users

@bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(client: Client, message: Message):
    # Check permission
    if not await is_admin(message.from_user.id):
        await message.reply_text("❌ You are not authorized to use this command.")
        return

    # Must reply to a forwarded message from channel
    if not message.reply_to_message or not message.reply_to_message.forward_from_chat:
        await message.reply_text("❌ Please reply to a *forwarded* message from your Channel.")
        return

    users = get_all_users()
    total = len(users)
    done = 0
    failed = 0

    status = await message.reply_text(f"📢 Broadcasting to {total} users...")

    for uid in users:
        try:
            # Forward message
            fwd_msg = await client.forward_messages(
                chat_id=uid,
                from_chat_id=message.chat.id,
                message_ids=message.reply_to_message.id
            )

            # Pin it with notification
            await client.pin_chat_message(
                chat_id=uid,
                message_id=fwd_msg.id,
                disable_notification=False  # ✅ notification ON
            )

            done += 1
        except Exception as e:
         #   print(f"❌ Failed for {uid}: {e}")
            failed += 1

        await asyncio.sleep(0.1)

    await status.edit_text(
        f"✅ **Broadcast Finished**\n\n👥 Total: {total}\n✅ Sent: {done}\n❌ Failed: {failed}"
    )
