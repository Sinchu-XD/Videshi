from pyrogram import Client, filters
from pyrogram.types import Message
from bson import ObjectId
from bson.errors import InvalidId
from Bot import bot
from Database import files_col, get_sudo_list
from Config import Config

async def is_authorized(user_id: int) -> bool:
    sudoers = await get_sudo_list()
    return user_id in sudoers or user_id == Config.OWNER_ID

@bot.on_message(filters.command("delfile") & filters.private)
async def delete_file_handler(client: Client, message: Message):
    user_id = message.from_user.id

    if not await is_authorized(user_id):
        await message.reply_text("❌ You don't have permission to use this command.")
        return

    if len(message.command) < 2:
        await message.reply_text("Usage:\n`/delfile <file_id>`")
        return

    file_id = message.command[1]

    try:
        result = files_col.delete_one({"_id": ObjectId(file_id)})
        if result.deleted_count:
            await message.reply_text("✅ File deleted successfully.")
        else:
            await message.reply_text("❌ No file found with that ID.")
    except InvalidId:
        await message.reply_text("❌ Invalid file ID format.")

@bot.on_message(filters.command("delallfiles") & filters.private)
async def delete_all_files_handler(client: Client, message: Message):
    user_id = message.from_user.id

    if not await is_authorized(user_id):
        await message.reply_text("❌ You don't have permission to use this command.")
        return

    result = files_col.delete_many({})
    await message.reply_text(f"✅ Deleted `{result.deleted_count}` files from the database.")
  
