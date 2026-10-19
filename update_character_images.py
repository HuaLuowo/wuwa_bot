
import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import requests
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

TARGETS = [
    "奧古斯塔", "尤諾", "嘉貝莉娜", "達妮婭",
    "蕾貝卡", "洛瑟菈", "露西", "緋雪",
    "秧秧·玄翎", "穗穗", "清宵", "景燃", "鎖暝"
]

API = "https://api.encore.moe"
IMAGE_HOST = "https://api-v2.encore.moe"

NAME_FIELDS = ("name", "Name", "character_name")
BACKUP_DIR = Path(__file__).resolve().parent


def normalize(name):
    return re.sub(r"[\s·・．._\-]", "", str(name)).casefold()


def find_values(data, target):
    values = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key.casefold() == target.casefold():
                values.append(value)
            values.extend(find_values(value, target))

    elif isinstance(data, list):
        for item in data:
            values.extend(find_values(item, target))

    return values


def collect_strings(data):
    if isinstance(data, str):
        return [data]

    if isinstance(data, list):
        result = []
        for item in data:
            result.extend(collect_strings(item))
        return result

    if isinstance(data, dict):
        result = []
        for item in data.values():
            result.extend(collect_strings(item))
        return result

    return []


def to_image_url(path):
    path = path.strip().replace("\\", "/")

    if path.startswith(("https://", "http://")):
        return path

    if "/resource/" in path:
        path = path[path.index("/resource/"):]
    elif path.startswith("Data/"):
        path = "/resource/" + path
    elif path.startswith("/Data/"):
        path = "/resource" + path
    else:
        return None

    return IMAGE_HOST + quote(path, safe="/")


def fetch_json(session, url):
    response = session.get(url, timeout=20)
    response.raise_for_status()
    return response.json()


def main():
    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("錯誤：找不到 MONGO_URI")
        return

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=10000
    )

    try:
        collection = client["wuwa_bot"]["characters"]

        print("正在讀取 Encore 角色列表...")
        data = fetch_json(session, f"{API}/zh-Hant/character")
        roles = data["roleList"]

        role_map = {}
        for role in roles:
            name = role.get("Name")
            role_id = role.get("Id")

            if name and role_id is not None:
                role_map.setdefault(normalize(name), []).append(role_id)

        print("正在檢查 MongoDB...")
        documents = list(collection.find({}))

        changes = []
        errors = []

        for name in TARGETS:
            matches = [
                doc for doc in documents
                if any(
                    normalize(doc[field]) == normalize(name)
                    for field in NAME_FIELDS
                    if isinstance(doc.get(field), str)
                )
            ]

            ids = role_map.get(normalize(name), [])

            if len(matches) != 1:
                errors.append(
                    f"{name}：MongoDB 找到 {len(matches)} 筆"
                )
                continue

            if len(ids) != 1:
                errors.append(
                    f"{name}：Encore 找到 {len(ids)} 個角色 ID"
                )
                continue

            try:
                detail = fetch_json(
                    session,
                    f"{API}/zh-Hant/character/{ids[0]}"
                )

                candidates = []

                for value in find_values(detail, "FormationRoleCard"):
                    for path in collect_strings(value):
                        url = to_image_url(path)
                        if url and url not in candidates:
                            candidates.append(url)

                if not candidates:
                    errors.append(f"{name}：沒有 FormationRoleCard")
                    continue

                doc = matches[0]

                changes.append({
                    "_id": str(doc["_id"]),
                    "name": name,
                    "old_exists": "character_image" in doc,
                    "old_image": doc.get("character_image"),
                    "new_image": candidates[0]
                })

                print(f"OK：{name}")

            except (requests.RequestException, ValueError) as error:
                errors.append(f"{name}：{error}")

        if errors or len(changes) != 13:
            print("\n檢查未通過，不更新資料庫。")
            for error in errors:
                print("-", error)
            return

        print("\n即將更新的圖片：")
        for change in changes:
            print(f"\n{change['name']}")
            print(f"原本：{change['old_image']}")
            print(f"更新：{change['new_image']}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / (
            f"character_image_backup_{timestamp}.json"
        )

        backup_path.write_text(
            json.dumps(changes, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print("\n已產生備份：", backup_path)
        print("目前尚未修改 MongoDB。")

        answer = input(
            "\n確認更新以上 13 筆？輸入 UPDATE 才會執行："
        ).strip()

        if answer != "UPDATE":
            print("已取消，MongoDB 沒有修改。")
            return

        updated = 0

        for change in changes:
            query = {"_id": ObjectId(change["_id"])}

            if change["old_exists"]:
                query["character_image"] = change["old_image"]
            else:
                query["character_image"] = {"$exists": False}

            result = collection.update_one(
                query,
                {"$set": {
                    "character_image": change["new_image"]
                }}
            )

            if result.matched_count != 1:
                print(
                    f"停止：{change['name']} 的資料已變動，"
                    "或無法找到原始資料。"
                )
                print("請保留備份檔，不要直接重新執行。")
                break

            updated += 1
            print(f"已更新：{change['name']}")

        print(f"\n本次成功寫入 {updated} / 13 筆")

        if updated == 13:
            print("13 隻角色圖片更新完成！")
        else:
            print("部分更新未完成，請保留備份並回報。")

    except (requests.RequestException, ValueError, KeyError) as error:
        print("執行失敗：", error)

    finally:
        client.close()
        session.close()

def check_rover():
    load_dotenv()
    client = MongoClient(os.getenv("MONGO_URI"))
    collection = client["wuwa_bot"]["characters"]

    for doc in collection.find({}):
        if "漂泊者" in str(doc.get("name", "")) and "導電" in str(doc.get("name", "")):
            print("ID：", doc["_id"])
            print("名稱：", doc.get("name"))
            print("圖片：", doc.get("character_image"))
            print("---")

    client.close()
if __name__ == "__main__":
    check_rover()
