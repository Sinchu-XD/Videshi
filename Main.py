import nest_asyncio
nest_asyncio.apply()

import asyncio
from Bot import bot        # Pyrogram client
from TelethonBot import app  # Telethon client

async def main():
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
