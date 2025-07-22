from pyrogram import filters
from pyrogram.types import Message
from Bot import bot
from Config import Config
from Database import get_all_users, get_sudo_list
import asyncio

async def is_admin(uid: int) -> bool:
    sudo_users = await get_sudo_list()
    return uid == Config.OWNER_ID or uid in sudo_users

@bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_forward(client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("❌ You are not authorized to use this command.")

    if not message.reply_to_message or not message.reply_to_message.forward_from_chat:
        return await message.reply("❌ Please reply to a *forwarded* message from your Channel.")

    users = await get_all_users()
    total = len(users)
    done = 0
    failed = 0

    status = await message.reply(f"📢 Broadcasting to {total} users...")

    for uid in users:
        try:
            await client.forward_messages(
                chat_id=uid,
                from_chat_id=message.chat.id,
                message_ids=message.reply_to_message.id
            )
            done += 1
        except Exception as e:
            print(f"❌ Failed for {uid}: {e}")
            failed += 1
        await asyncio.sleep(0.2)  # Avoid flood limit

    await status.edit_text(
        f"✅ **Broadcast Finished**\n\n👥 Total: {total}\n✅ Sent: {done}\n❌ Failed: {failed}"
    )
