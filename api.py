from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri)

db = mongo_client["wuwa_bot"]
characters_collection = db["characters"]

app = FastAPI()

def find_character_by_id(character_id):
    character = characters_collection.find_one({"id":character_id})
    if character is None:
        raise HTTPException(status_code=404, detail="找不到角色")
    return character

@app.get("/")
def home():
    return{"message": "Wuwa Bot API"}

@app.get("/characters/count")
def character_count():
    count = characters_collection.count_documents({})
    return {"count": count}

@app.get("/characters")
def get_characters():
    characters = characters_collection.find({})
    result = []
    for character in characters:
        character_data = {
            "id": character["id"],
            "name": character["name"],
            "rarity": character["rarity"],
            "attribute": character["attribute"],
            "weapon": character["weapon"]
        }
        result.append(character_data)
    return result

@app.get("/characters/{character_id}")
def get_character(character_id: int):
    character = find_character_by_id(character_id)
    character.pop("_id")
    return character


@app.get("/characters/{character_id}/skills")
def get_character_skills(character_id: int):
    character = find_character_by_id(character_id)
    return character["skills"]

@app.get("/characters/{character_id}/chains")
def get_character_chains(character_id: int):
    character = find_character_by_id(character_id)
    return character["chains"]

@app.get("/characters/{character_id}/breaches")
def get_character_breaches(character_id: int):
    character = find_character_by_id(character_id)
    return character["breaches"]