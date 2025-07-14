import os
import importlib
import asyncio
from Bot import bot

plugin_folder = "Plugins"

# Asynchronous function to load plugins
async def load_plugins():
    for filename in os.listdir(plugin_folder):
        if filename.endswith(".py"):
            importlib.import_module(f"{plugin_folder}.{filename[:-3]}")

# Initialize function to load plugins and run the bot
async def init():
    print(">> Bot Starting...")

    # Load plugins asynchronously
    await load_plugins()

    # Run the bot
    await bot.run()

# Main entry point
if __name__ == "__main__":
    # Create the event loop and run the init function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())  # Run the async init function until complete
