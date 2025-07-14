from datetime import datetime
import time
from pymongo import MongoClient
from bson import ObjectId
from Config import Config

db = MongoClient(Config.MONGO_URI).RichBot

users_collection = db.users
sudo_col = db.sudo_users
channel_col = db.required_channels
settings_collection = db.settings
files_col = db.files
config_col = db.config
blocked_col = db.blocked_users

# ✅ NEW bulk files collection
bulk_files_col = db.bulk_files

async def add_user(user_id: int, first_name: str, username: str = None):
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "username": username,
            "joined_on": datetime.utcnow()
        })

async def get_users_count() -> int:
    return users_collection.count_documents({})

def get_all_users():
    users = users_collection.find({}, {"user_id": 1})
    return [user["user_id"] for user in users]

async def add_blocked_user(user_id: int, duration_sec: int = 1200):
    unblock_time = int(time.time()) + duration_sec
    blocked_col.update_one(
        {"user_id": user_id},
        {"$set": {"unblock_time": unblock_time}},
        upsert=True
    )

async def remove_blocked_user(user_id: int):
    blocked_col.delete_one({"user_id": user_id})

async def get_blocked_user(user_id: int):
    user = blocked_col.find_one({"user_id": user_id})
    if user and user["unblock_time"] > time.time():
        return user["unblock_time"]
    elif user:
        await remove_blocked_user(user_id)
    return None

async def add_sudo(user_id: int):
    if not sudo_col.find_one({"user_id": user_id}):
        sudo_col.insert_one({"user_id": user_id})

async def remove_sudo(user_id: int):
    sudo_col.delete_one({"user_id": user_id})

async def get_sudo_list():
    return [x["user_id"] for x in sudo_col.find().to_list(length=1000)]

async def add_channel(username: str):
    if not channel_col.find_one({"username": username}):
        channel_col.insert_one({"username": username})

async def remove_channel(username: str):
    channel_col.delete_one({"username": username})

async def get_channels():
    return [x["username"] for x in channel_col.find().to_list(length=1000)]

async def save_file(user_id: int, chat_id: int, message_id: int, file_type: str):
    doc = {
        "user_id": user_id,
        "chat_id": chat_id,
        "message_id": message_id,
        "file_type": file_type,
        "time": datetime.utcnow()
    }
    insert = files_col.insert_one(doc)
    return str(insert.inserted_id)

async def get_file_by_id(file_id: str):
    return files_col.find_one({"_id": ObjectId(file_id)})

# ✅ NEW: Save a bulk album
async def save_bulk_file(user_id: int, files: list) -> str:
    bulk_doc = {
        "user_id": user_id,
        "files": files,
        "time": datetime.utcnow()
    }
    insert = files_col.insert_one(bulk_doc)
    return str(insert.inserted_id)
    
async def get_bulk_file_by_id(ref_id: str):
    return bulk_files_col.find_one({"_id": ObjectId(ref_id)})

async def set_force_check(value: bool):
    settings_collection.update_one(
        {"_id": "force_check"},
        {"$set": {"value": value}},
        upsert=True
    )

async def get_force_check():
    setting = settings_collection.find_one({"_id": "force_check"})
    return setting["value"] if setting else False

async def set_main_channel(channel: str):
    config_col.update_one(
        {"_id": "main_channel"},
        {"$set": {"value": channel}},
        upsert=True
    )

async def get_main_channel() -> str:
    data = config_col.find_one({"_id": "main_channel"})
    return data["value"] if data else None
