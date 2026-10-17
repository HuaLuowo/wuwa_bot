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

def get_chinese_weapon_name(english_name):
    weapon_id = weapons_mapping.get(english_name)
    if weapon_id is None:
        return None
    else:
        weapon_data = weapons_collection.find_one({"id": weapon_id})
        if weapon_data is None:
            return None
        else:
            return weapon_data["name"]
print(get_chinese_weapon_name("Ages of Harvest"))
print(get_chinese_weapon_name("Kumokiri"))
print(get_chinese_weapon_name("dodogy"))

recommended_weapons = [
    "Ages of Harvest",
    "Kumokiri",
    "Wildfire Mark"
]
for weapon in recommended_weapons:
    print(get_chinese_weapon_name(weapon))

weapon_info = {
    "name": weapon["name"],
    "rank": weapon["rank"],
    "damage": weapon["damage"]
}