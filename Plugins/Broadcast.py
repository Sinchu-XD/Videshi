from pyrogram import filters
from pyrogram.types import Message
from Bot import bot
from Bot.TelethonClient import telethon_client
from Config import Config
from Database import get_all_users, get_sudo_list
from telethon.errors import ChatAdminRequiredError
import asyncio

async def is_admin(uid: int) -> bool:
    sudo_users = await get_sudo_list()
    return uid == Config.OWNER_ID or uid in sudo_users

@bot.on_message(filters.command("broadcast") & filters.private)
async def hybrid_broadcast(client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("❌ You are not authorized to use this command.")

    if not message.reply_to_message or not message.reply_to_message.forward_from_chat:
        return await message.reply("❌ Please reply to a *forwarded* message from your Channel.")

    users = get_all_users()
    total = len(users)
    done = 0
    failed = 0

    status = await message.reply(f"📢 Broadcasting to {total} users...")

    for uid in users:
        try:
            # Forward using Pyrogram
            fwd_msg = await client.forward_messages(uid, message.reply_to_message.id, message.chat.id)

            # Pin using Telethon MTProto
            await telethon_client.pin_message(uid, fwd_msg.id, notify=True)

            done += 1
        except ChatAdminRequiredError:
            print(f"❌ Can't pin in chat {uid} (need admin rights)")
            failed += 1
        except Exception as e:
            print(f"❌ Failed for {uid}: {e}")
            failed += 1

        await asyncio.sleep(0.1)

    await status.edit(
        f"✅ **Broadcast Finished**\n\n👥 Total: {total}\n✅ Sent: {done}\n❌ Failed: {failed}"
    )
