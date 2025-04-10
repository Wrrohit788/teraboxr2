from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from config import MONGO_DB_URL as MONGO_DB_URI 

mongo = MongoClient(MONGO_DB_URI)
db = mongo.GEEK

async def update_token(user_id, token, time):
    await db.tokens.update_one({"user_id": user_id}, {"$set": {"info": {"token": token, "time": time}}}, upsert=True)
    
async def get_token(user_id):
    x = await db.tokens.find_one({"user_id": user_id})
    if x:
        return [x["info"]["token"], x["info"]["time"]]
    return [None, None]

async def set_verification_token(user_id, token):
    await db.verify.update_one({"user_id": user_id}, {"$set": {"token": token}}, upsert=True)
    
async def get_verification_token(user_id):
    x = await db.verify.find_one({"user_id": user_id})
    if x:
        return x["token"]
    return None
