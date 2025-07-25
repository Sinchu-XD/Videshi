from pyrogram import Client, filters
from pyrogram.types import Message
from Bot import bot
from Config import Config
from Database import (
    add_channel,
    remove_channel,
    get_channels,
    set_main_channel,
    get_main_channel
)
from .Store import is_admin as owner_or_sudo

def extract_channel_input(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("https://t.me/"):
        raw = raw.replace("https://t.me/", "")
    elif raw.startswith("t.me/"):
        raw = raw.replace("t.me/", "")
    return raw

@bot.on_message(filters.command("addchannel") & filters.group & filters.user(Config.OWNER_ID))
async def add_channel_cmd(client: Client, message: Message):
    
    if len(message.command) < 2:
        await message.reply_text("Usage: /addchannel <channel_link or @username>")
        return

    ch = extract_channel_input(" ".join(message.command[1:]))
    await add_channel(ch)
    await message.reply_text(f"✅ Added `{ch}` to required channel list.")
    

@bot.on_message(filters.command("rmchannel") & filters.group & filters.user(Config.OWNER_ID))
async def remove_channel_cmd(client: Client, message: Message):
    
    if len(message.command) < 2:
        await message.reply_text("Usage: /rmchannel <channel_link or @username>")
        return

    ch = extract_channel_input(" ".join(message.command[1:]))
    await remove_channel(ch)
    await message.reply_text(f"❌ Removed `{ch}` from required channel list.")

@bot.on_message(filters.command("channelslist") & filters.group & filters.user(Config.OWNER_ID))
async def list_channels_cmd(client: Client, message: Message):
    
    channels = await get_channels()
    if not channels:
        await message.reply_text("📭 No channels saved.")
        return

    msg = "**📢 Required Channels:**\n" + "\n".join([f"- `{ch}`" for ch in channels])
    await message.reply_text(msg)

@bot.on_message(filters.command("mainchannel") & filters.group & filters.user(Config.OWNER_ID))
async def set_or_get_main_channel_cmd(client: Client, message: Message):
    

    if len(message.command) < 2:
        main_ch = await get_main_channel()
        if not main_ch:
            await message.reply_text("🚫 Main channel not set.")
        else:
            await message.reply_text(f"📢 **Main Channel:** `{main_ch}`")
        return

    ch = extract_channel_input(" ".join(message.command[1:]))
    await set_main_channel(ch)
    await message.reply_text(f"✅ Set `{ch}` as the **Main Channel**.")
  
