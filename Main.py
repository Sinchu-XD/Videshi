import os
import importlib
import asyncio
from Bot import bot

plugin_folder = "Plugins"

async def load_plugins():
    for filename in os.listdir(plugin_folder):
        if filename.endswith(".py"):
            importlib.import_module(f"{plugin_folder}.{filename[:-3]}")

async def init():
    print(">> Bot Starting...")
    await load_plugins()
    await bot.run()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
