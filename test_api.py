import requests
import json
import re
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)
db = client["wuwa_bot"]
characters_collection = db["characters"]

url = "https://api.encore.moe/zh-Hant/character"
response = requests.get(url, timeout = 10)
data = response.json()

characters = data["roleList"]
print("API角色數量: ", len(characters))

ids = []

for character in characters:
    ids.append(character["Id"])
print("角色總數：", len(ids))
print("不重複 ID 數量：", len(set(ids)))

character_list = []

for character in characters[:1]:
    character_data = {
        "id": character["Id"],
        "name": character["Name"],
        "rarity": character["QualityId"],
        "attribute": character["Element"]["Name"],
        "weapon": character["WeaponType"]["Name"],
        "image": character["RoleHeadIcon"]
    }
    character_list.append(character_data)

with open("api_characters.json", "w", encoding="utf-8") as file:
    json.dump(character_list, file, ensure_ascii=False, indent=4)

item_name_cache = {}
full_character_list = []
failed_character_ids = []
for character in characters:
    character_id = character["Id"]
    detail_url = f"https://api.encore.moe/zh-Hant/character/{character_id}"
    try:
        detail_response = requests.get(detail_url, timeout=10)
        detail_response.raise_for_status()
        detail_data = detail_response.json()
        english_url = f"https://api.encore.moe/en/character/{character_id}"
        english_response = requests.get(english_url, timeout = 10)
        english_response.raise_for_status()
        english_data = english_response.json()
        english_name = english_data["Name"]["Content"]
        url_name = english_name.lower().replace(" ","-")
        if url_name == "shorekeeper":
            url_name = "the-shorekeeper"
        guide_url = f"https://www.prydwen.gg/wuthering-waves/characters/{url_name}"
    except Exception as e:
        print("角色資料取得失敗: ", e)
        failed_character_ids.append(character_id)
        continue

    skills = detail_data.get("Skills")
    clean_skills = []
    for skill in skills:
        description = skill["SkillDescribe"].replace("<br>", "\n")
        description = re.sub(r"<.*?>", "", description)
        description = "\n".join(line.strip()for line in description.split("\n"))
        description = re.sub(r"\n{3,}", "\n\n", description)
        clean_skill = {
            "id": skill["SkillId"],
            "name": skill["SkillName"],
            "type": skill["SkillType"],
            "description": description,
            }
        clean_skills.append(clean_skill)

    resonant_chain = detail_data.get("ResonantChain")
    clean_chains = []
    for chain in resonant_chain:
        description = chain["AttributesDescription"]
        description = re.sub(r"<.*?>", "", description)
        clean_chain = {
            "index" : chain["GroupIndex"],
            "name" : chain["NodeName"],
            "description": description
        }
        clean_chains.append(clean_chain)

    breaches = detail_data.get("Breaches")
    clean_breaches = []

    for breach in breaches:
        if breach["BreachLevel"] == 0:
            continue

        materials = []

        for material in breach["BreachConsume"]:
            material_id = material["Key"]
            quantity = material["Value"]

            if material_id in item_name_cache:
                material_name = item_name_cache[material_id]
            else:
                try:
                    item_url = f"https://api.encore.moe/zh-Hant/item/{material_id}"
                    item_response = requests.get(item_url, timeout=10)
                    item_response.raise_for_status()
                    item_data = item_response.json()
                    material_name = item_data["Name"]
                    item_name_cache[material_id] = material_name
                except Exception as e:
                    print("素材資料取得失敗", e)
                    material_name = None

            clean_material = {
                "material_id": material_id,
                "material_name": material_name,
                "quantity": quantity
            }
            materials.append(clean_material)

        clean_breach = {
            "level": breach["BreachLevel"],
            "materials": materials
        }
        clean_breaches.append(clean_breach)

    introduction = detail_data["Introduction"]["Content"]
    introduction = re.sub(r"<.*?>", "", introduction)
    clean_tags = []
    for tag in detail_data["Tags"]:
        clean_tag = {
            "name": tag["TagName"],
            "description": tag["TagDesc"]
        }
        clean_tags.append(clean_tag)

    profile = {
        "birthday": detail_data["favorRole"]["Birthday"]["Content"],
        "sex": detail_data["favorRole"]["Sex"]["Content"],
        "country": detail_data["favorRole"]["Country"]["Content"],
        "influence": re.sub("<.*?>", "", detail_data["favorRole"]["Influence"]["Content"])
    }
    
    new_character_data = {
    "id": detail_data["Id"],
    "name": detail_data["Name"]["Content"],
    "name_en": english_name,
    "guide_url": guide_url,
    "rarity": detail_data["QualityId"],
    "attribute": detail_data["ElementName"],
    "weapon" : detail_data["WeaponTypeName"],
    "image" : detail_data["RoleHeadIconLarge"],
    "character_image": detail_data.get("FormationRoleCard") or detail_data.get("RolePortrait"),
    "introduction": introduction,
    "tags": clean_tags,
    "profile": profile,
    "skills": clean_skills,
    "chains": clean_chains,
    "breaches": clean_breaches
}
    full_character_list.append(new_character_data)

    if not new_character_data["character_image"]:
        new_character_data.pop("character_image")
    existing_character = characters_collection.find_one(
        {"id": new_character_data["id"]}
    )

    if existing_character is not None:
        if existing_character.get("character_image"):
            new_character_data.pop("character_image", None)
        if existing_character.get("guide_url") and existing_character["guide_url"] != guide_url and english_name != "Shorekeeper":
            print("攻略網址不同: ", english_name)
            new_character_data["guide_url"] = existing_character["guide_url"]
        characters_collection.update_one(
            {"_id": existing_character["_id"]},
            {"$set": new_character_data}
        )
    else:
        characters_collection.insert_one(new_character_data)

print("完整角色數量: ", len(full_character_list))
for character in full_character_list:
    if not character["skills"]:
        print("技能資料異常: ", character["name"])

for character in full_character_list:
    if not character["chains"]:
        print("共鳴鏈資料異常: ", character["name"])

for character in full_character_list:
    if not character["breaches"]:
        print("突破資料異常", character["name"])

for character in full_character_list:
    for breach in character["breaches"]:
        for material in breach["materials"]:
            if material["material_name"] is None:
                print(
                    "素材名稱異常: ",
                    character["name"],
                    material["material_id"]
                )

print("MongoDB角色數量: ", characters_collection.count_documents({}))
print("取得API失敗的角色ID: ", failed_character_ids)