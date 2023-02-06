from motor.motor_asyncio import AsyncIOMotorClient
from config import DATABASE_URL, DATABASE_NAME

client = AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]
col = db["users"]


async def get_user(user_id):

    user_id = int(user_id)

    user = await col.find_one({"user_id": user_id})

    if not user:
        res = {
            "user_id": user_id,
            "shortener_api": None,
            "header_text": "",
            "footer_text": "",
            "username": None,
            "banner_image": None,
            "is_banner_image": True,
            "is_username": True,
            "is_header_text": True,
            "is_footer_text": True,
        }

        user = await col.insert_one(res)

    return user

async def update_user_info(user_id, value:dict):
    user_id = int(user_id)
    myquery = {"user_id": user_id}
    newvalues = { "$set": value }
    await col.update_one(myquery, newvalues)

async def total_users_count():
    count = await col.count_documents({})
    return count

async def get_all_users():
    all_users = col.find({})
    return all_users

async def delete_user(user_id):
    await col.delete_one({'user_id': int(user_id)})