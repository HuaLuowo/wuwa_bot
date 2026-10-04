import json
import discord
import os
from dotenv import load_dotenv
from commands.character import CharacterCommands
from commands.weapon import WeaponCommands
from discord.ext import commands
from pymongo import MongoClient

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri)
db = mongo_client["wuwa_bot"]
weapons = db["weapons"]
characters_collection = db["characters"]
intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree


async def setup_hook():
    await client.add_cog(CharacterCommands(characters_collection))
    await client.add_cog(WeaponCommands(weapons))
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
version = "0.2.1"
description = "提供鳴潮角色、武器、聲骸與攻略查詢"

print(f"目前支援角色數量: {characters_collection.count_documents({})}")

print("本Discord bot名稱:",bot_name)
print("作者:",author)
print("版本:",version)
print("功能描述:",description)

client.run(token)
