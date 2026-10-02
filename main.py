import json
import discord
import os
from dotenv import load_dotenv
from commands.character import CharacterCommands, get_character
from discord.ext import commands

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree

with open("characters.json", "r", encoding="utf-8") as character_file:
    characters = json.load(character_file)

async def setup_hook():
    await client.add_cog(CharacterCommands(characters))
client.setup_hook = setup_hook
@client.event
async def on_ready():
    await tree.sync()
    print("Bot 已上線")

@tree.command(name="測試", description="滷蛋很有錢")
async def test_command(interactrion):
    await interactrion.response.send_message("滷蛋很有錢")


bot_name = "鳴潮 Discord bot"
author = "HuaLuowo"
version = "0.0.65"
description = "提供鳴潮角色、武器、聲骸與攻略查詢"

print(characters)
print(f"目前支援角色數量: {len(characters)}")
def show_characters(characters_list):
    for character in characters_list:
        print(f"支援角色: {character}")
show_characters(characters)

def search_character(characters_list, character_name):
    if character_name in characters_list:
        print(f"找到角色: {character_name}")
        print(f"屬性: {characters_list[character_name]["attribute"]}")
        print(f"武器: {characters_list[character_name]["weapon"]}")
    else:
        print(f"查無此角色: {character_name}")

def delete_character(characters_list, character_name):
    if character_name in characters_list:
        del characters_list[character_name]
        print(f"已刪除角色: {character_name}")
    else:
        print(f"查無此角色: {character_name}")
def add_character(characters_list, character_name,attribute, weapon):
    characters_list[character_name] = {"attribute": attribute, "weapon": weapon}
def save_characters(characters_list):
    with open("characters.json", "w", encoding="utf-8") as character_file:
        json.dump(characters_list, character_file, ensure_ascii=False, indent=4)

print("本Discord bot名稱:",bot_name)
print("作者:",author)
print("版本:",version)
print("功能描述:",description)

character_name = input("請輸入角色名稱：")
character_data = get_character(characters, character_name)
if character_data is not None:
    print(f"角色: {character_name}")
    print(f"屬性: {character_data["attribute"]}")
    print(f"武器: {character_data["weapon"]}")
    print(f"稀有度: {character_data['rarity']}")
else:
    print("找不到角色")

client.run(token)
