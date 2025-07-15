from pyrogram import Client
from Config import Config

bot = Client(
    "RichFeatureBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

from telethon import TelegramClient

app = TelegramClient(
    "TelethonSession",
    Config.API_ID,
    Config.API_HASH
)

# This will keep the Telethon session active
app.start(bot_token=Config.BOT_TOKEN)
