import asyncio
import os
import importlib
from Bot import bot       # Pyrogram Client
from Bot import app  # Telethon Client

plugin_folder = "Plugins"

def load_plugins():
    for filename in os.listdir(plugin_folder):
        if filename.endswith(".py"):
            importlib.import_module(f"{plugin_folder}.{filename[:-3]}")

async def main():
    print(">> Loading plugins...")
    load_plugins()

    print(">> Starting clients...")

    # Start Telethon client
    await app.start()

    # Start Pyrogram client (runs forever)
    await bot.start()

    # Wait until both clients disconnect
    await asyncio.gather(
        app.run_until_disconnected(),
        bot.idle()  # Keeps Pyrogram client running
    )

if __name__ == "__main__":
    asyncio.run(main())
    
