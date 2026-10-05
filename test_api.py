import requests
import json
import re

url = "https://api.encore.moe/zh-Hant/character"

response = requests.get(url, timeout = 10)

print(response.status_code)

data = response.json()

characters = data["roleList"]
print("API角色數量: ", len(characters))

ids = []

for character in characters:
    ids.append(character["Id"])
print("角色總數：", len(ids))
print("不重複 ID 數量：", len(set(ids)))

character_list = []

for character in characters:
    character_data = {
        "id": character["Id"],
        "name": character["Name"],
        "rarity": character["QualityId"],
        "attribute": character["Element"]["Name"],
        "weapon": character["WeaponType"]["Name"],
        "image": character["RoleHeadIcon"]
    }
    character_list.append(character_data)
print("整理後角色數量: ", len(character_list))

with open("api_characters.json", "w", encoding="utf-8") as file:
    json.dump(character_list, file, ensure_ascii=False, indent=4)

item_name_cache = {}
full_character_list = []
for character in characters[:5]:
    character_id = character["Id"]
    detail_url = f"https://api.encore.moe/zh-Hant/character/{character_id}"
    print("詳細資料網址", detail_url)
    detail_response = requests.get(detail_url, timeout=10)
    print("狀態碼: ", detail_response.status_code)
    detail_response.raise_for_status()
    detail_data = detail_response.json()
    print("目前角色: ", detail_data["Name"]["Content"])

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
                item_url = f"https://api.encore.moe/zh-Hant/item/{material_id}"
                item_response = requests.get(item_url, timeout=10)
                item_response.raise_for_status()
                item_data = item_response.json()
                material_name = item_data["Name"]
                item_name_cache[material_id] = material_name

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
    new_character_data = {
    "id": detail_data["Id"],
    "name": detail_data["Name"]["Content"],
    "rarity": detail_data["QualityId"],
    "attribute": detail_data["ElementName"],
    "weapon" : detail_data["WeaponTypeName"],
    "image" : detail_data["RoleHeadIconLarge"],
    "character_image": detail_data["RolePortrait"],
    "skills": clean_skills,
    "chains": clean_chains,
    "breaches": clean_breaches
}
    full_character_list.append(new_character_data)

print("完整角色數量: ", len(full_character_list))
for character in full_character_list:
    print(
        character["id"],
        character["name"],
        len(character["skills"]),
        len(character["chains"]),
        len(character["breaches"])
    )
    
