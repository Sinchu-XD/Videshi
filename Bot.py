from pyrogram import Client
from Config import Config

bot = Client(
    "RichFeatureBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)
