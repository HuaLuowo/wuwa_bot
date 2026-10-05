import requests
from bs4 import BeautifulSoup


list_url = "https://wuthering.gg/zh-Hant/characters"
def parse_character(html):
    soup = BeautifulSoup(html, "html.parser")
    description_tag = soup.find(
        "meta",
        attrs={"name": "description"}
    )
    description = description_tag.get("content")
    parts = description.split(" ")
    name = parts[1]
    rarity = int(parts[3])
    attribute = parts[5]
    weapon = parts[7]
    character_data = {
        "name": name,
        "rarity": rarity,
        "attribute": attribute,
        "weapon": weapon
    }
    return character_data

list_response = requests.get(list_url, timeout=10)
list_response.encoding = "utf-8"
soup = BeautifulSoup(list_response.text, "html.parser")
print(list_response.status_code)
print("/zh-Hant/characters/jinhsi" in list_response.text)
print(soup.title.text)

links = soup.find_all("a")
print(len(links))

character_urls = set()
for link in links:
    href = link.get("href")
    if href and href.startswith("/zh-Hant/characters/"):
        character_urls.add(href)
print(character_urls)
print("角色網址數量: ", len(character_urls))

characters_data = []
test_paths = sorted(character_urls)[:3]
for test_path in test_paths:
    test_url = "https://wuthering.gg" + test_path
    test_response = requests.get(test_url, timeout=10)
    test_response.encoding = "utf-8"

    result = parse_character(test_response.text)
    characters_data.append(result)
print(characters_data)
print("成功收集: ", len(characters_data), "個角色")
