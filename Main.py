from Bot import bot
import os
import importlib

plugin_folder = "Plugins"

for filename in os.listdir(plugin_folder):
    if filename.endswith(".py"):
        importlib.import_module(f"{plugin_folder}.{filename[:-3]}")

if __name__ == "__main__":
    print(">> Bot Starting...")
    bot.run()
  
