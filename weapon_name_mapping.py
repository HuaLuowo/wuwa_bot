import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import os

url = "https://api.encore.moe/en/weapon"
response = requests.get(url,timeout=10)
response.raise_for_status()
data = response.json()

weapons = data["weapons"]
print("英文武器總數:", len(weapons))

weapons_mapping ={}

for weapon in weapons:
    weapons_mapping[weapon["Name"]] = weapon["Id"]
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["wuwa_bot"]
weapons_collection = db["weapons"]

english_name = "Kumokiri"
weapon_id = weapons_mapping[english_name]
weapon_data = weapons_collection.find_one({"id": weapon_id})
print(english_name, "->", weapon_id, "->", weapon_data["name"])

def get_chinese_weapon_name(english_name):
    weapon_id = weapons_mapping.get(english_name)
    weapon_data = weapons_collection.find_one({"id": weapon_id})
    return weapon_data["name"]
print(get_chinese_weapon_name("Ages of Harvest"))
print(get_chinese_weapon_name("Kumokiri"))