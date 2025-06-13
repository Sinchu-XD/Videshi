import os

class Config:
    API_ID = int(os.getenv("API_ID", 6067591))
    API_HASH = os.getenv("API_HASH", "94e17044c2393f43fda31d3afe77b26b")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "7946373751:AAEnaR6L6-8d9cYYlOCS1UqmXSjRXFjARVI")
    MONGO_URI = os.getenv("MONGO_URL", "mongodb+srv://Sinchu:Sinchu@sinchu.qwijj.mongodb.net/?retryWrites=true&w=majority&appName=Sinchu")
    OWNER_ID = int(os.getenv("OWNER_ID", "7862043458"))
    LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", -1002716981360))
    BOT_USERNAME = "InstagramStuffsBot"
  
