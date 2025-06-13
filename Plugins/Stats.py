from pyrogram import Client, filters
from Config import Config
from Database import get_users_count, files_col, channel_col, get_sudo_list
from Bot import bot

@bot.on_message(filters.command("stats"))
async def bot_stats(client: Client, message):
    user_id = message.from_user.id
    sudoers = await get_sudo_list()

    if user_id not in sudoers and user_id != Config.OWNER_ID:
        return await message.reply_text("❌ You are not authorized to view stats.")

    total_users = await get_users_count()
    total_files = await files_col.count_documents({})
    total_channels = await channel_col.count_documents({})
    total_sudos = len(sudoers)

    text = (
        "**📊 Bot Statistics**\n\n"
        f"👥 Total Users: `{total_users}`\n"
        f"📂 Total Files: `{total_files}`\n"
        f"📢 Required Channels: `{total_channels}`\n"
        f"👮‍♂️ Sudo Users: `{total_sudos}`"
    )
    await message.reply_text(text)
  
