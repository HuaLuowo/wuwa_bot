import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)

client.admin.command("ping")
print("MongoDB 連線成功！")

db = client["wuwa_bot"]
with open("characters.json", "r", encoding= "utf-8") as character_file:
    characters_data = json.load(character_file)
print(type(characters_data))
print(list(characters_data.items())[:1])
characters = db["characters"]
for name, data in characters_data.items():
    print(name,data)
    data["name"] = name
    existing_character = characters.find_one({"name": name})
    if existing_character == None:
        characters.insert_one(data)
print(characters.count_documents({}))


weapons = db["weapons"]

with open("weapons.json", "r", encoding= "utf-8") as weapon_file:
    weapons_data = json.load(weapon_file)
for name, data in weapons_data.items():
    print(name, data)
    data["name"] = name
    existing_weapon = weapons.find_one({"name" : name})
    if existing_weapon == None:
        weapons.insert_one(data)
    else:
        weapons.update_one(
            {"name": name},
            {"$set": data}
        )

print(weapons.count_documents({}))
print(weapons.find_one({"name": "時和歲稔"}))