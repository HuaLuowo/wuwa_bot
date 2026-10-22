import discord
from discord import app_commands
from discord.ext import commands
from character_autocomplete import character_autocomplete as shared_character_autocomplete

class CharacterMaterials(commands.Cog):
    def __init__(self, bot, character_collection):
        self.bot = bot
        self.character_collection = character_collection

    async def character_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ):
        return await shared_character_autocomplete(
            interaction, current, self.character_collection
        )
    @app_commands.command(name = "角色突破材料", description="查詢角色突破材料總覽")
    @app_commands.rename(character_name = "角色")
    @app_commands.autocomplete(character_name= character_autocomplete)
    async def character_materials(self, interaction: discord.Interaction, character_name:str):    
        character = self.character_collection.find_one(
            {"name": character_name}
        )
        if character is None:
            await interaction.response.send_message("找不到角色資料")
            return
        breaches = character.get("breaches", [])
        materials_total = {}
        for breach in breaches:
            for material in breach.get("materials", []):
                name = material["material_name"]
                quantity = material["quantity"]
                materials_total[name] = materials_total.get(name, 0) + quantity
        embed = discord.Embed(
            title= f"{character_name} 突破材料總覽",
            color= discord.Color.blue()
        )
        for name, quantity in materials_total.items():
            embed.add_field(
                name = name,
                value=f"× {quantity}",
                inline= False
            )
        await interaction.response.send_message(embed=embed)