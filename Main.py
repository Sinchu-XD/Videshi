import os
import importlib
from Bot import bot       # Pyrogram Client
from Bot import app  # Telethon Client
import asyncio

plugin_folder = "Plugins"

def load_plugins():
    for filename in os.listdir(plugin_folder):
        if filename.endswith(".py"):
            importlib.import_module(f"{plugin_folder}.{filename[:-3]}")

async def main():
    print(">> Loading plugins...")
    load_plugins()

    print(">> Starting clients...")

    await app.start()
    await bot.start()

    await asyncio.gather(
        app.run_until_disconnected(),
        bot.idle()
    )

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
