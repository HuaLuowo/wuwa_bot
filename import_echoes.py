import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)
db = client["wuwa_bot"]
echoes_collection = db["echoes"]

url = "https://api.encore.moe/zh-Hant/echo"
response = requests.get(url=url, timeout=15)
response.raise_for_status()

data = response.json()
echoes = data["Echo"]

cost_mapping = {
    0:1,
    1:3,
    2:4,
    3:4
}

print(f"聲骸總數: {len(echoes)}")
print("所有 Rarity 數值:", sorted({echo["Rarity"] for echo in echoes}))

for echo in echoes:
    echo_id = echo["Id"]
    detail_url = f"https://api.encore.moe/zh-Hant/echo/{echo_id}"

    detail_response = requests.get(detail_url, timeout=10)
    detail_response.raise_for_status()
    detail_data = detail_response.json()
    skill = detail_data.get("Skill") or {}
    name = echo.get("Name")

    if not name or name.startswith("MonsterInfo_"):
        name = detail_data.get("MonsterName") or ""
    if not name or name.startswith("MonsterInfo_"):
        name = f"未知聲骸_{echo_id}"
    echo_data = {
        "id": detail_data["MonsterId"],
        "name": name,
        "intensity":(
            "特殊boss"
            if detail_data["Rarity"] == 3
            else(detail_data.get("Handbook") or {}).get("Intensity")or "未知"
        ),
        "cost": cost_mapping.get(detail_data["Rarity"]),
        "phantom_type": echo.get("PhantomType"),
        "location": (detail_data.get("Handbook") or{}).get("Place")or "未知",
        "element": detail_data["Element"],
        "image": detail_data["Icon"],
        "sets": [
            {
                "name": group["Name"],
                "effects": [
                    {
                        "pieces": effect["Key"],
                        "description": effect["EffectDescription"]
                    }
                    for effect in group["Fetters"]
                ]
            }
            for group in echo.get("FetterGroups", [])
        ],
        "skill": {
            "description": skill.get("DescriptionEx")or "查無技能資料",
            "cooldown": skill.get("SkillCD")
        }
    }

    result = echoes_collection.update_one(
        {"id": echo_data["id"]},
        {"$set": echo_data},
        upsert= True
    )
    print(f"已匯入聲骸: {echo_data['name']}, ID:{echo_data['id']}")
print("MongoDB 聲骸總數:", echoes_collection.count_documents({}))