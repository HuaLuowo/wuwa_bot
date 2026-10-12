import requests
import re
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["wuwa_bot"]
weapons_collection = db["weapons"]

url = "https://api.encore.moe/zh-Hant/weapon"
response = requests.get(url=url, timeout=10)
data = response.json()
weapons = data["weapons"]
print(f"武器總數: {len(weapons)}")
success_count = 0
for weapon in weapons:
    weapon_id = weapon["Id"]
    detail_url = f"https://api.encore.moe/zh-Hant/weapon/{weapon['Id']}"
    try:
        detail_response = requests.get(url=detail_url, timeout=10)
        detail_response.raise_for_status()
        detail_data = detail_response.json()
    except(requests.RequestException, ValueError) as e:
        print("取得武器資料失敗：", weapon["Name"], e)
        continue

    properties = detail_data["Properties"]
    if len(properties) != 2:
        print("需要檢查: ", weapon["Name"])
        continue
    try:
        growth_values = properties[0]["GrowthValues"]
        initial_attack = float(growth_values[0]["Value"].replace("%", ""))
        max_attack = float(growth_values[-1]["Value"].replace("%", ""))
    except(KeyError, IndexError, TypeError, ValueError) as e:
        print("攻擊數值轉換失敗:", weapon["Name"], e)
        continue
    try:
        secondary_name = properties[1]["Name"]
        secondary_growth = properties[1]["GrowthValues"]
        initial_secondary = secondary_growth[0]["Value"]
        clean_secondary = initial_secondary.replace("%", "")
        initial_secondary_value = float(clean_secondary)
        max_secondary = secondary_growth[-1]["Value"]
        clean_max_secondary = max_secondary.replace("%", "")
        max_secondary_value = float(clean_max_secondary)
    except(KeyError, IndexError, TypeError, ValueError) as e:
         print("副屬性轉換失敗：", weapon["Name"], e)
         continue

    effect_name = detail_data["ResonName"]
    effect_discription = detail_data["Desc"]
    effect_discription = re.sub(r"<[^>]+>", "", effect_discription)

    weapon_data = {
        "id": weapon_id,
        "name": detail_data["WeaponName"],
        "type": detail_data["WeaponTypeName"],
        "rarity": detail_data["QualityId"],
        "initial": {
            "attack": initial_attack,
            "secondary_stat": {
                "name": secondary_name,
                "value": initial_secondary_value
            }
        },
        "max": {
            "attack": max_attack,
            "secondary_stat": {
                "name": secondary_name,
                "value": max_secondary_value
            }
        },
        "effect": {
            "name": effect_name,
            "description": effect_discription
        }
    }

    weapons_collection.update_one(
        {"name": weapon_data["name"]},
        {"$set": weapon_data},
        upsert= True
    )
    success_count += 1
    print("已匯入:", weapon_data["name"])
print(f"成功匯入: {success_count}/{len(weapons)}")
print("MongoDB武器總數: ", weapons_collection.count_documents({}))
client.close()