import os
import importlib
from Bot import bot 

plugin_folder = "Plugins"

# Function to load plugins
def load_plugins():
    for filename in os.listdir(plugin_folder):
        if filename.endswith(".py"):
            importlib.import_module(f"{plugin_folder}.{filename[:-3]}")

# Initialize function to load plugins and run the bot
def init():
    print(">> Bot Starting...")

    # Load plugins
    load_plugins()

    # Run the bot (Let Pyrogram manage the event loop)
    bot.run()

# Main entry point
if __name__ == "__main__":
    init()  # Run everything without manually con
trolling the event loop
