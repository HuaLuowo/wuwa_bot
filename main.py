import json
import discord
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

with open("characters.json", "r", encoding="utf-8") as character_file:
    characters = json.load(character_file)

def get_character(characters_list, character_name):
    if character_name in characters_list:
        return characters_list[character_name]
    else:
        return None

@client.event
async def on_ready():
    await tree.sync()
    print("Bot 已上線")

@tree.command(name="測試", description="滷蛋很有錢")
async def test_command(interactrion):
    await interactrion.response.send_message("滷蛋很有錢")
async def character_autocomplete(interaction,current:str):
    result = []
    for character in characters:
        if current in character:
            result.append(discord.app_commands.Choice(
                name = character,
                value = character
            ))
    return result[:25]
@tree.command(name="角色", description="查詢角色資料")
@discord.app_commands.autocomplete(character_name = character_autocomplete)
async def search(interaction, character_name:str):
    data = get_character(characters, character_name)
    if data is not None:
        if data["attribute"] == "熱熔":
            card_color = discord.Color.red()
        elif data["attribute"] == "衍射":
            card_color = discord.Color.yellow()
        else:
            card_color = discord.Color.blue()
        card = discord.Embed(title = character_name, color = card_color)
        card.add_field(name = "屬性", value = data["attribute"])
        card.add_field(name = "武器", value = data["weapon"])
        card.add_field(name="稀有度", value="★" * data["rarity"])
        await interaction.response.send_message(embed = card)
    else:
       await interaction.response.send_message("找不到角色")
bot_name = "鳴潮 Discord bot"
author = "HuaLuowo"
version = "0.0.5"
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
